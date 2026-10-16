import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.deduplication import ParticipantDeduplicator
from api.models import Participant, TptIndividual, IneligibleIndividual


class Command(BaseCommand):
    help = (
        "Scan and merge duplicate participant records in the Central Backend "
        "using multi-tier matching rules."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply the deduplication merges to the central database. By default, dry-run is performed."
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
        cohort = options["cohort"]
        output_json = options["json"]
        dry_run = not apply_changes

        if dry_run and not output_json:
            self.stdout.write(self.style.WARNING("=" * 80))
            self.stdout.write(self.style.WARNING(" CENTRAL BACKEND DEDUPLICATION: RUNNING IN DRY-RUN MODE"))
            self.stdout.write(self.style.WARNING(" Pass --apply to execute merge and purge duplicate records."))
            self.stdout.write(self.style.WARNING("=" * 80 + "\n"))

        models_map = {}
        if cohort in ["all", "participants"]:
            models_map["Central Participants"] = Participant
        if cohort in ["all", "tpt"]:
            models_map["Central TPT Individuals"] = TptIndividual
        if cohort in ["all", "ineligible"]:
            models_map["Central Ineligible Individuals"] = IneligibleIndividual

        overall_results = {
            "timestamp": timezone.now().isoformat(),
            "dry_run": dry_run,
            "cohorts": {}
        }

        for label, model_cls in models_map.items():
            dedup = ParticipantDeduplicator(model_class=model_cls)
            res = dedup.deduplicate_all(dry_run=dry_run)
            overall_results["cohorts"][label] = res
            
            if not output_json:
                clusters = res.get("reports", [])
                total_clusters = res.get("total_clusters", 0)
                total_dups = res.get("total_duplicates_detected", 0)

                if total_clusters == 0:
                    self.stdout.write(self.style.SUCCESS(f"  [OK] {label}: 0 duplicates found. All records are unique."))
                    continue

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

        if output_json:
            self.stdout.write(json.dumps(overall_results, indent=2, default=str))
        else:
            self.stdout.write("\n" + "=" * 80)
            status_text = "DRY-RUN COMPLETE" if dry_run else "DEDUPLICATION COMPLETE"
            self.stdout.write(self.style.SUCCESS(f" [{status_text}] Central Backend Summary:"))
            for ch_name, ch_data in overall_results["cohorts"].items():
                self.stdout.write(
                    f"   - {ch_name}: {ch_data['total_clusters']} duplicate clusters, "
                    f"{ch_data['total_duplicates_detected']} redundant records "
                    f"({'would merge' if dry_run else 'merged & purged'})"
                )
            self.stdout.write("=" * 80 + "\n")
