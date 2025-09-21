from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone

# ---------------------------
# Custom User Manager
# ---------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError('Email is required')
        if not username:
            raise ValueError('Username is required')
        if not password:
            raise ValueError('Password is required')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None):
        if not password:
            raise ValueError('Superuser must have a password')
        user = self.create_user(email, username, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

# ---------------------------
# Custom User
# ---------------------------
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_users_groups',  # unique name
        blank=True,
        help_text='The groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_users_permissions',  # unique name
        blank=True,
        help_text='Specific permissions for this user.'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

# ---------------------------
# Follow Model
# ---------------------------
class Follow(models.Model):
    follower = models.ForeignKey(
        CustomUser,
        related_name='users_follower_set',  # unique name
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        CustomUser,
        related_name='users_following_set',  # unique name
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.follower} follows {self.following}"
