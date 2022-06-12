from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import CustomUsersManager


class Users(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    username = None
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField(max_length=40, unique=True)
    password = models.CharField(max_length=80)

    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    objects = CustomUsersManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    list_filter = ('staff', 'admin')
    list_display = ('user_id', 'first-name', 'last_name')
    ordering = ('user_id')

    @property
    def is_staff(self):
        return self.staff


class Projects(models.Model):
    class Types(models.TextChoices):
        BE = 'back-end'
        FE = 'front-end'
        IOS = 'IOS'
        ANDROID = 'Android'

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=400)
    type = models.CharField(max_length=40, choices=Types.choices)
    author_user = models.ForeignKey(to=Users,
                                    on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Contributors(models.Model):
    class Role(models.TextChoices):
        AUTHOR = 'Author'
        CONTRIB = 'Contributor'

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(to=Users, on_delete=models.CASCADE)
    project = models.ForeignKey(to=Projects, on_delete=models.CASCADE)
    permission = models.CharField(max_length=100)
    role = models.CharField(max_length=11, choices=Role.choices)

    class Meta:
        unique_together = ['user', 'project']


class Issues(models.Model):
    class Priorities(models.TextChoices):
        H = 'High'
        M = 'Medium'
        L = 'Low'

    class Tags(models.TextChoices):
        B = 'Bug'
        I = 'Improvement'
        T = 'Task'

    class Statuses(models.TextChoices):
        TD = 'To-do'
        WIP = 'Work In Progress'
        DONE = 'Done'

    issue_id = models.BigAutoField(primary_key=True)

    title = models.CharField(max_length=200)
    desc = models.CharField(max_length=500)
    tag = models.CharField(max_length=40, choices=Tags.choices)

    priority = models.CharField(max_length=40, choices=Priorities.choices)
    project = models.ForeignKey(to=Projects, on_delete=models.CASCADE)

    status = models.CharField(max_length=40, choices=Statuses.choices)
    author_user = models.ForeignKey(to=Users, on_delete=models.CASCADE, related_name='issue_author')
    assignee_user = models.ForeignKey(to=Users, on_delete=models.CASCADE, related_name='issue_assignee')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comments(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=400)
    author_user_id = models.ForeignKey(to=Users,
                                       on_delete=models.CASCADE, )
    issue = models.ForeignKey(to=Issues, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
