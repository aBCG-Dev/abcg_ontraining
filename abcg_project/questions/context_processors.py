"""
Template context processors for global template variables.
Provides all_districts and all_tb_units to every template.
"""

import time
import copy
from questions.models import Participant, TptIndividual, IneligibleIndividual
from questions.locations_data import JURISDICTION_DATA, get_base_hierarchy

_HIERARCHY_CACHE = {"data": None, "expires_at": 0}
_CAMPAIGN_PERIODS_CACHE = {"data": None, "expires_at": 0}
CACHE_TTL_SECONDS = 300  # 5 minutes in-memory cache


def clear_location_cache(*args, **kwargs):
    """Invalidates the in-memory location and campaign cache upon data mutation."""
    _HIERARCHY_CACHE["data"] = None
    _HIERARCHY_CACHE["expires_at"] = 0
    _CAMPAIGN_PERIODS_CACHE["data"] = None
    _CAMPAIGN_PERIODS_CACHE["expires_at"] = 0


from django.db.models.signals import post_save, post_delete
try:
    from questions.models import StudySite
    post_save.connect(clear_location_cache, sender=StudySite)
    post_delete.connect(clear_location_cache, sender=StudySite)
except Exception:
    pass


def get_site_campaign_periods_dict():
    """
    Returns a dictionary mapping tb_unit -> campaign_period_display string
    from active StudySite records and historical defaults.
    Cached for 5 minutes to prevent redundant SELECT queries on every page request.
    """
    now = time.time()
    if _CAMPAIGN_PERIODS_CACHE["data"] is not None and now < _CAMPAIGN_PERIODS_CACHE["expires_at"]:
        return dict(_CAMPAIGN_PERIODS_CACHE["data"])

    periods = {
        "Tiruvallur TU": "Jan 2025 - Mar 2025"
    }
    try:
        from questions.models import StudySite
        for s in StudySite.objects.filter(is_active=True).only('tb_unit', 'district', 'launch_date', 'concluding_date'):
            if s.tb_unit:
                periods[s.tb_unit] = s.campaign_period_display
            if s.district and s.district not in periods:
                periods[s.district] = s.campaign_period_display
    except Exception:
        pass

    _CAMPAIGN_PERIODS_CACHE["data"] = dict(periods)
    _CAMPAIGN_PERIODS_CACHE["expires_at"] = now + CACHE_TTL_SECONDS
    return periods


def get_location_hierarchy():
    """
    Returns structured location hierarchy {State: {District: [TB_Units]}}.
    Cached in memory for 5 minutes to avoid 10 distinct queries per request across 5 tables.
    """
    now = time.time()
    if _HIERARCHY_CACHE["data"] is not None and now < _HIERARCHY_CACHE["expires_at"]:
        return copy.deepcopy(_HIERARCHY_CACHE["data"])

    hierarchy = get_base_hierarchy()

    try:
        from questions.models import UserProfile, StudySite
        sources = [
            StudySite.objects.filter(is_active=True).values_list('state', 'district', 'tb_unit').distinct(),
            Participant.objects.values_list('state', 'district', 'tb_unit').distinct(),
            TptIndividual.objects.values_list('state', 'district', 'tb_unit').distinct(),
            IneligibleIndividual.objects.values_list('state', 'district', 'tb_unit').distinct(),
            UserProfile.objects.values_list('state', 'district', 'tb_unit').distinct(),
        ]
        for src in sources:
            for state, district, tb_unit in src:
                if not state or not district or not tb_unit:
                    continue
                if state.upper() == 'GLOBAL' or district.upper() == 'ALL DISTRICTS' or tb_unit.upper() == 'ALL TB UNITS':
                    continue
                state_str = str(state).strip()
                dist_str = str(district).strip()
                tbu_str = str(tb_unit).strip()
                
                if state_str not in hierarchy:
                    hierarchy[state_str] = {}
                if dist_str not in hierarchy[state_str]:
                    hierarchy[state_str][dist_str] = []
                if tbu_str not in hierarchy[state_str][dist_str]:
                    hierarchy[state_str][dist_str].append(tbu_str)
    except Exception:
        pass

    _HIERARCHY_CACHE["data"] = copy.deepcopy(hierarchy)
    _HIERARCHY_CACHE["expires_at"] = now + CACHE_TTL_SECONDS
    return hierarchy


def navbar_choices(request):
    """
    Provides dropdown options for navbar filters.
    Available in all templates.
    """
    # Retrieve structured locations hierarchy (cached)
    hierarchy = get_location_hierarchy()

    # Extract all districts and TB units directly from hierarchy without hitting database
    districts_set = set()
    tb_units_set = set()
    for s_data in hierarchy.values():
        for d_name, tu_list in s_data.items():
            districts_set.add(d_name)
            tb_units_set.update(tu_list)
    all_districts = sorted(districts_set)
    all_tb_units = sorted(tb_units_set)

    user_states = []
    user_districts = []
    user_tb_units = []
    selected_state = ""
    selected_district = ""
    selected_tb_unit = ""
    user_districts = []
    user_tb_units = []
    selected_state = ""
    selected_district = ""
    selected_tb_unit = ""

    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)
        role = getattr(profile, "role", "Project Nurse") if profile else ""

        # Update session from GET parameters if present, and handle cascades
        if 'state' in request.GET:
            new_state = request.GET.get('state', '')
            if new_state != request.session.get('selected_state', ''):
                request.session['selected_state'] = new_state
                request.session['selected_district'] = ''
                request.session['selected_tb_unit'] = ''
        
        if 'district' in request.GET:
            new_district = request.GET.get('district', '')
            if new_district != request.session.get('selected_district', ''):
                request.session['selected_district'] = new_district
                request.session['selected_tb_unit'] = ''
                
        if 'tb_unit' in request.GET:
            request.session['selected_tb_unit'] = request.GET.get('tb_unit', '')

        selected_state = request.session.get('selected_state', '')
        selected_district = request.session.get('selected_district', '')
        selected_tb_unit = request.session.get('selected_tb_unit', '')

        # Enforce boundaries based on user role
        if role not in ["Super Admin", "Admin"]:
            selected_state = profile.state if profile else "Tamil Nadu"
        if role in ["Nodal Officer", "Doctor", "Project Nurse"]:
            selected_district = profile.district if profile else ""
        if role in ["Doctor", "Project Nurse"]:
            selected_tb_unit = profile.tb_unit if profile else ""

        # Cascading choices based on active filter selections and roles
        if role in ["Super Admin", "Admin"]:
            user_states = sorted(list(hierarchy.keys()))
            
            if selected_state and selected_state in hierarchy:
                user_districts = sorted(list(hierarchy[selected_state].keys()))
            else:
                districts_set = set()
                for s in hierarchy.values():
                    districts_set.update(s.keys())
                user_districts = sorted(list(districts_set))
                
            if selected_district:
                tb_units_set = set()
                for s_name, s_data in hierarchy.items():
                    if selected_state and s_name != selected_state:
                        continue
                    if selected_district in s_data:
                        tb_units_set.update(s_data[selected_district])
                user_tb_units = sorted(list(tb_units_set))
            elif selected_state and selected_state in hierarchy:
                tb_units_set = set()
                for dist_data in hierarchy[selected_state].values():
                    tb_units_set.update(dist_data)
                user_tb_units = sorted(list(tb_units_set))
            else:
                tb_units_set = set()
                for s_data in hierarchy.values():
                    for dist_data in s_data.values():
                        tb_units_set.update(dist_data)
                user_tb_units = sorted(list(tb_units_set))

        elif role == "Nodal Officer":
            state_val = profile.state if profile else "Tamil Nadu"
            dist_val = profile.district if profile else ""
            user_states = [state_val]
            user_districts = [dist_val]
            
            if state_val in hierarchy and dist_val in hierarchy[state_val]:
                user_tb_units = sorted(hierarchy[state_val][dist_val])
            else:
                user_tb_units = [profile.tb_unit] if profile else []

        else:  # Doctor, Project Nurse
            user_states = [profile.state] if profile else ["Tamil Nadu"]
            user_districts = [profile.district] if profile else []
            user_tb_units = [profile.tb_unit] if profile else []

        # Calculate active backlog count for the user's scope (cached in session for 30 seconds)
        cache_key = f"_unsynced_{selected_state}_{selected_district}_{selected_tb_unit}"
        cached_tuple = request.session.get(cache_key)
        now_ts = time.time()
        if cached_tuple and isinstance(cached_tuple, (list, tuple)) and len(cached_tuple) == 2 and (now_ts - cached_tuple[1]) < 30:
            total_unsynced = cached_tuple[0]
        else:
            try:
                p_qs = Participant.objects.filter(synced=False)
                t_qs = TptIndividual.objects.filter(synced=False)
                i_qs = IneligibleIndividual.objects.filter(synced=False)

                if role != "Super Admin":
                    p_qs = p_qs.filter(state=profile.state)
                    t_qs = t_qs.filter(state=profile.state)
                    i_qs = i_qs.filter(state=profile.state)

                    if role in ["Nodal Officer", "Doctor", "Project Nurse"]:
                        p_qs = p_qs.filter(district=profile.district)
                        t_qs = t_qs.filter(district=profile.district)
                        i_qs = i_qs.filter(district=profile.district)

                    if role in ["Doctor", "Project Nurse"]:
                        p_qs = p_qs.filter(tb_unit=profile.tb_unit)
                        t_qs = t_qs.filter(tb_unit=profile.tb_unit)
                        i_qs = i_qs.filter(tb_unit=profile.tb_unit)

                # Apply active session filters
                if selected_state:
                    p_qs = p_qs.filter(state=selected_state)
                    t_qs = t_qs.filter(state=selected_state)
                    i_qs = i_qs.filter(state=selected_state)
                if selected_district:
                    p_qs = p_qs.filter(district=selected_district)
                    t_qs = t_qs.filter(district=selected_district)
                    i_qs = i_qs.filter(district=selected_district)
                if selected_tb_unit:
                    p_qs = p_qs.filter(tb_unit=selected_tb_unit)
                    t_qs = t_qs.filter(tb_unit=selected_tb_unit)
                    i_qs = i_qs.filter(tb_unit=selected_tb_unit)

                total_unsynced = p_qs.count() + t_qs.count() + i_qs.count()
                request.session[cache_key] = [total_unsynced, now_ts]
            except Exception:
                total_unsynced = 0

    else:
        total_unsynced = 0

    import json
    return {
        'all_districts': all_districts,
        'all_tb_units': all_tb_units,
        'user_states': user_states,
        'user_districts': user_districts,
        'user_tb_units': user_tb_units,
        'selected_state': selected_state,
        'selected_district': selected_district,
        'selected_tb_unit': selected_tb_unit,
        'total_unsynced': total_unsynced,
        'location_hierarchy_json': json.dumps(hierarchy),
        'jurisdiction_data_json': json.dumps(JURISDICTION_DATA),
        'site_campaign_periods_json': json.dumps(get_site_campaign_periods_dict()),
    }

