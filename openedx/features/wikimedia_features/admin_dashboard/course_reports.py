# Create your views here.
from django.http.response import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.courses import get_course_by_id
from opaque_keys.edx.keys import CourseKey
from common.djangoapps.util.cache import cache, cache_if_anonymous
from openedx.core.djangoapps.catalog.utils import get_programs_with_type
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from lms.djangoapps.instructor.views.instructor_dashboard import (
    _section_data_download
)
from lms.djangoapps.courseware.courses import (
    get_courses,
    sort_by_announcement,
    sort_by_start_date
)
from common.djangoapps.edxmako.shortcuts import render_to_response


@login_required
@ensure_csrf_cookie
@cache_if_anonymous()
def generate_report(request):
    """
    Render "find courses" page.  The course selection work is done in courseware.courses.
    """
    courses_list = []
    sections = {"key":{}}
    if not settings.FEATURES.get('ENABLE_COURSE_DISCOVERY'):
        courses_list = get_courses(request.user)

        if configuration_helpers.get_value("ENABLE_COURSE_SORTING_BY_START_DATE",
                                        settings.FEATURES["ENABLE_COURSE_SORTING_BY_START_DATE"]):
            courses_list = sort_by_start_date(courses_list)
        else:
            courses_list = sort_by_announcement(courses_list)

    course = get_course_by_id(courses_list[0].id, depth=0)
    #Add marketable programs to the context.

    access = {
        'admin': request.user.is_staff,
        'instructor': bool(has_access(request.user, 'instructor', courses_list[0])),
    }
    sections["key"] = _section_data_download(course, access)
    return render_to_response(
        "course_report/course-reports.html",
        {
            'courses': courses_list,
            'section_data': sections,
        }
    )
