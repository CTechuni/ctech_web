from app.core.database import Base
from app.modules.users.models import Role, User, Profile
from app.modules.auth.models import TokenBlocklist
from app.modules.communities.models import Community
from app.modules.courses.models import Course
from app.modules.events.models import Event
from app.modules.content.models import EducationalContent, ThematicArea, LearningLevel
from app.modules.specialties.models import Specialty
from app.modules.technologies.models import Technology
from app.modules.mentoring_sessions.models import MentoringSession
from app.modules.notifications.models import Notification