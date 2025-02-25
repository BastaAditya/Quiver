from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from chat.models import ChatInfo

from .managers import BeaverManager
from .constants import ImageConstant, ResetConstants

import logging as log

User = get_user_model()


class Beaver(models.Model):
    phone_number_regex = RegexValidator(
        regex="^[1-9][0-9]{9}$", message="Not a valid phone number",
    )
    gender_choice = [("M", "Male"), ("F", "Female"), ("N", "Cannot Specify")]
    objects = BeaverManager()
    user = models.OneToOneField(User, related_name="users", on_delete=models.CASCADE)
    gender = models.CharField(
        max_length=1, choices=gender_choice, default="Cannot Specify"
    )
    bio = models.TextField(
        help_text="Enter your profile bio", default="Hello everyone", blank=True
    )
    date_of_birth = models.DateField(auto_now=False)
    profile_photo = models.ImageField(
        upload_to="images/profile/",
        help_text="Profile Photo",
        default=ImageConstant.defaultImage.value,
    )
    phone = models.BigIntegerField(validators=[phone_number_regex])
    friends = models.ManyToManyField("self", blank=True)
    college = models.TextField(null=True)
    company = models.TextField(null=True)
    industry = models.TextField(null=True)

    class Meta:
        verbose_name_plural = "Beavers"

    def __str__(self):
        return self.user.username

    @classmethod
    def make_friend(cls, creator, friend):
        creator.friends.add(friend)
        beaver = Beaver.objects.filter(user=creator.user).first()
        chatinfo = ChatInfo.objects.filter(
            member1=beaver, member2=friend
        ) | ChatInfo.objects.filter(member2=beaver, member1=friend)
        log.error(chatinfo)
        if not chatinfo:
            ChatInfo.createChatInformation(creator, friend)

    @classmethod
    def remove_friend(cls, creator, friend):
        friend1 = cls.objects.get(user=creator)
        friend1.friends.remove(friend)


class ResetPasswordModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    securityCode = models.IntegerField(null=True, blank=True)  # Min should be 100000
    timeCreated = models.DateTimeField(auto_now_add=True)
    # Remove this entry if time becomes more than 5 mins

    class Meta:
        verbose_name_plural = "Reset Passwords"

    def __str__(self):
        return self.user.username

    # Before checking if security code is valid or not, use this function
    # TODO : Try to override a method instead of making 2 calls

    @classmethod
    def validateCode(cls, securityCode, user):
        resetPasswordInstance, created = cls.objects.get_or_create(user=user)
        getCreated = resetPasswordInstance.timeCreated
        minuteDiff = (timezone.now() - getCreated) / timezone.timedelta(minutes=1)
        # Time limit has been exceeded then delete
        if minuteDiff > 5:
            resetPasswordInstance.delete()
            return {"status": False, "error": ResetConstants.timeExceeded}
        else:
            if securityCode != resetPasswordInstance.securityCode:
                return {"status": False, "error": ResetConstants.noMatch}
            else:
                resetPasswordInstance.delete()
                return {"status": True, "error": None}
