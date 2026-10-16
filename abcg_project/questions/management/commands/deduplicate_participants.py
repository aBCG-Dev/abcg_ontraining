import json
import subprocess
import sys
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from questions.deduplication import ParticipantDeduplicator


class Command(BaseCommand):
    help = (
        "Identify and merge duplicate participant records entered multiple times "
        "using multi-tier matching rules (Nikshay ID, Phone + Name, Name + DOB/Age + Gender)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply the deduplication merges directly to the database. By default, dry-run is performed."
        )
        parser.add_argument(
            "--scope",
            type=str,
            choices=["field", "central", "all"],
            default="field",
            help="Target database scope to scan and deduplicate (field, central, or all). Default is field."
        )
        parser.add_argument(
            "--cohort",
            type=str,
            choices=["all", "participants", "tpt", "ineligible"],
            default="all",
            help="Target cohort models to process."
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Print machine-readable JSON output of the deduplication results."
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        scope = options["scope"]
        cohort = options["cohort"]
        output_json = options["json"]
        dry_run = not apply_changes

        if dry_run and not output_json:
            self.stdout.write(self.style.WARNING("=" * 80))
            self.stdout.write(self.style.WARNING(" RUNNING IN DRY-RUN MODE (No database records will be modified)"))
            self.stdout.write(self.style.WARNING(" Pass --apply to execute merge and purge duplicate records."))
            self.stdout.write(self.style.WARNING("=" * 80 + "\n"))

        overall_results = {
            "timestamp": timezone.now().isoformat(),
            "dry_run": dry_run,
            "scope": scope,
            "scopes_processed": {}
        }

        # 1. Process Field App Database
        if scope in ["field", "all"]:
            self._process_field_scope(cohort, dry_run, output_json, overall_results)

        # 2. Process Central Backend Database via subprocess
        if scope in ["central", "all"]:
            self._process_central_scope(cohort, apply_changes, output_json, overall_results)

        if output_json:
            self.stdout.write(json.dumps(overall_results, indent=2, default=str))
        else:
            self.stdout.write("\n" + "=" * 80)
            status_text = "DRY-RUN COMPLETE" if dry_run else "DEDUPLICATION COMPLETE"
            self.stdout.write(self.style.SUCCESS(f" [{status_text}] Summary:"))
            for sc_name, data in overall_results["scopes_processed"].items():
                self.stdout.write(f"   Scope: {sc_name.upper()}")
                if isinstance(data, dict):
                    for ch_name, ch_data in data.items():
                        if isinstance(ch_data, dict) and "total_clusters" in ch_data:
                            self.stdout.write(
                                f"     - {ch_name}: {ch_data['total_clusters']} duplicate clusters, "
                                f"{ch_data['total_duplicates_detected']} redundant records "
                                f"({'would merge' if dry_run else 'merged & purged'})"
                            )
            self.stdout.write("=" * 80 + "\n")

    def _process_field_scope(self, cohort, dry_run, output_json, overall_results):
        from questions.models import Participant, TptIndividual, IneligibleIndividual
        
        models_map = {}
        if cohort in ["all", "participants"]:
            models_map["Participant (General Cohort)"] = Participant
        if cohort in ["all", "tpt"]:
            models_map["TptIndividual (TPT Cohort)"] = TptIndividual
        if cohort in ["all", "ineligible"]:
            models_map["IneligibleIndividual (Screened Ineligible)"] = IneligibleIndividual

        scope_report = {}
        if not output_json:
            self.stdout.write(self.style.MIGRATE_HEADING(">>> Scanning Field App Database (questions)..."))

        for label, model_cls in models_map.items():
            dedup = ParticipantDeduplicator(model_class=model_cls)
            res = dedup.deduplicate_all(dry_run=dry_run)
            scope_report[label] = res
            
            if not output_json:
                self._print_cohort_results(label, res, dry_run)

        overall_results["scopes_processed"]["field_app"] = scope_report

    def _process_central_scope(self, cohort, apply_changes, output_json, overall_results):
        if not output_json:
            self.stdout.write(self.style.MIGRATE_HEADING("\n>>> Invoking Central Backend Deduplication Command..."))

        central_dir = os.path.join(os.getcwd(), "central_backend")
        manage_path = os.path.join(central_dir, "manage.py")
        if not os.path.exists(manage_path):
            overall_results["scopes_processed"]["central_backend"] = {"error": "central_backend/manage.py not found"}
            return

        cmd = [sys.executable, "manage.py", "deduplicate_participants", "--cohort", cohort, "--json"]
        if apply_changes:
            cmd.append("--apply")

        env = os.environ.copy()
        env["DJANGO_SETTINGS_MODULE"] = "central_project.settings"

        try:
            res = subprocess.run(cmd, cwd=central_dir, env=env, capture_output=True, text=True, check=True)
            central_data = json.loads(res.stdout)
            overall_results["scopes_processed"]["central_backend"] = central_data.get("cohorts", {})
            
            if not output_json:
                for label, c_res in central_data.get("cohorts", {}).items():
                    self._print_cohort_results(label, c_res, not apply_changes)
        except Exception as e:
            if not output_json:
                self.stdout.write(self.style.WARNING(f"  Note: Failed to query central backend: {e}"))
            overall_results["scopes_processed"]["central_backend"] = {"error": str(e)}

    def _print_cohort_results(self, label, res, dry_run):
        clusters = res.get("reports", [])
        total_clusters = res.get("total_clusters", 0)
        total_dups = res.get("total_duplicates_detected", 0)

        if total_clusters == 0:
            self.stdout.write(self.style.SUCCESS(f"  [OK] {label}: 0 duplicates found. All records are unique."))
            return

        self.stdout.write(self.style.WARNING(
            f"  [!] {label}: Found {total_clusters} duplicate clusters ({total_dups} duplicate records)"
        ))
        
        for idx, rep in enumerate(clusters[:10], start=1):
            master_id = rep["master_study_id"]
            name = rep.get("master_name", "")
            dup_count = rep["duplicate_count"]
            merged_ids = rep.get("merged_study_ids", [])
            fields_enriched = ", ".join(rep.get("fields_updated", [])) or "None (Master already complete)"
            
            action_desc = "Would merge into" if dry_run else "Merged into"
            self.stdout.write(
                f"      Cluster #{idx}: {name} ({dup_count + 1} occurrences) -> "
                f"{action_desc} Master '{master_id}'"
            )
            self.stdout.write(f"        Redundant IDs: {', '.join(merged_ids[:5])}{'...' if len(merged_ids) > 5 else ''}")
            self.stdout.write(f"        Fields Enriched: {fields_enriched}")

        if len(clusters) > 10:
            self.stdout.write(f"      ... and {len(clusters) - 10} more duplicate clusters.")
