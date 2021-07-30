"""
Unit tests for course_goals djangoapp
"""

from unittest import mock

from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from common.djangoapps.student.models import CourseEnrollment
from edx_toggles.toggles.testutils import override_waffle_flag
from lms.djangoapps.course_goals.models import CourseGoal
from lms.djangoapps.course_goals.toggles import COURSE_GOALS_NUMBER_OF_DAYS_GOALS
from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from openedx.features.course_experience import ENABLE_COURSE_GOALS

EVENT_NAME_ADDED = 'edx.course.goal.added'
EVENT_NAME_UPDATED = 'edx.course.goal.updated'

User = get_user_model()


@override_waffle_flag(ENABLE_COURSE_GOALS, active=True)
@override_waffle_flag(COURSE_GOALS_NUMBER_OF_DAYS_GOALS, active=True)
class TestCourseGoalsAPI(SharedModuleStoreTestCase):
    """
    Testing the Course Goals API.
    """

    def setUp(self):
        # Create a course with a verified track
        super().setUp()
        self.course = CourseFactory.create(emit_signals=True)

        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'password')
        CourseEnrollment.enroll(self.user, self.course.id)

        self.client = APIClient(enforce_csrf_checks=True)
        self.client.login(username=self.user.username, password=self.user.password)
        self.client.force_authenticate(user=self.user)

        self.apiUrl = reverse('course-home-save-course-goal')

    def save_course_goal(self, number, subscribed):
        """
        Sends a post request to set a course goal and returns the response.
        """
        post_data = {
            'course_id': self.course.id,
            'user': self.user.username,
        }
        if number is not None:
            post_data['number_of_days_with_visits_per_week_goal'] = number
        if subscribed is not None:
            post_data['subscribed_to_goal_reminders'] = subscribed

        response = self.client.post(self.apiUrl, post_data)
        return response

    @mock.patch('lms.djangoapps.course_goals.handlers.segment.track')
    @override_settings(LMS_SEGMENT_KEY="foobar")
    def test_add_goal(self, segment_call):
        """ Ensures a correctly formatted post succeeds."""
        self.save_course_goal(1, True)
        segment_call.assert_called_once_with(self.user.id, EVENT_NAME_ADDED, {
            'courserun_key': str(self.course.id),
            'number_of_days_with_visits_per_week_goal': 1,
            'subscribed_to_goal_reminders': True,
            'goal_key': 'unsure',
        })

        current_goals = CourseGoal.objects.filter(user=self.user, course_key=self.course.id)
        assert len(current_goals) == 1
        assert current_goals[0].number_of_days_with_visits_per_week_goal == 1
        assert current_goals[0].subscribed_to_goal_reminders is True

    @mock.patch('lms.djangoapps.course_goals.handlers.segment.track')
    @override_settings(LMS_SEGMENT_KEY="foobar")
    def test_update_goal(self, segment_call):
        """ Ensures that repeatedly saving a course goal does not create new instances of the goal. """
        self.save_course_goal(1, True)
        segment_call.assert_called_with(self.user.id, EVENT_NAME_ADDED, {
            'courserun_key': str(self.course.id),
            'number_of_days_with_visits_per_week_goal': 1,
            'subscribed_to_goal_reminders': True,
            'goal_key': 'unsure',
        })

        self.save_course_goal(3, True)
        segment_call.assert_called_with(self.user.id, EVENT_NAME_UPDATED, {
            'courserun_key': str(self.course.id),
            'number_of_days_with_visits_per_week_goal': 3,
            'subscribed_to_goal_reminders': True,
            'goal_key': 'unsure',
        })

        self.save_course_goal(5, False)
        segment_call.assert_called_with(self.user.id, EVENT_NAME_UPDATED, {
            'courserun_key': str(self.course.id),
            'number_of_days_with_visits_per_week_goal': 5,
            'subscribed_to_goal_reminders': False,
            'goal_key': 'unsure',
        })

        current_goals = CourseGoal.objects.filter(user=self.user, course_key=self.course.id)
        assert len(current_goals) == 1
        assert current_goals[0].number_of_days_with_visits_per_week_goal == 5
        assert current_goals[0].subscribed_to_goal_reminders is False

    def test_add_without_required_arguments(self):
        """ Ensures if required arguments are not provided, post does not succeed. """
        response = self.save_course_goal(None, None)
        assert len(CourseGoal.objects.filter(user=self.user, course_key=self.course.id)) == 0
        self.assertContains(
            response=response,
            text="'number_of_days_with_visits_per_week_goal' and 'subscribed_to_goal_reminders' are required.",
            status_code=400
        )

    def test_add_invalid_goal(self):
        """ Ensures an incorrectly formatted post does not succeed. """
        response = self.save_course_goal('notnumber', False)
        assert response.status_code == 400
        assert len(CourseGoal.objects.filter(user=self.user, course_key=self.course.id)) == 0
