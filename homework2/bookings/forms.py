"""Forms for registering users and authenticating sign-in attempts."""

from types import SimpleNamespace

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Movie, Seat


User = get_user_model()


class RegistrationForm(UserCreationForm):  # pylint: disable=too-many-ancestors
    """Validate new username/password details without saving until requested."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Configure Django's built-in user fields for registration."""

        model = User
        fields = ("username",)


class SignInForm(forms.Form):
    """Authenticate credentials and expose one generic failure message."""

    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, request=None, **kwargs):
        """Keep the request for authentication, with a session for unit use."""
        super().__init__(*args, **kwargs)
        self.request = request or SimpleNamespace(session={})
        self.user = None

    def clean(self):
        """Authenticate supplied credentials without creating a session."""
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if username and password:
            self.user = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user is None:
                raise forms.ValidationError("Invalid username or password.")
        return cleaned_data

    def get_user(self):
        """Return the authenticated account, or ``None`` after failure."""
        return self.user


class SeatBookingForm(forms.Form):
    """Validate that a submitted seat belongs to its selected movie."""

    movie = forms.ModelChoiceField(
        queryset=Movie.objects.all(),  # pylint: disable=no-member
        widget=forms.HiddenInput,
    )
    seat = forms.ModelChoiceField(
        queryset=Seat.objects.all(),  # pylint: disable=no-member
        widget=forms.HiddenInput,
    )

    def clean(self):
        """Reject a real seat that is outside the selected movie inventory."""
        cleaned_data = super().clean()
        movie = cleaned_data.get("movie")
        seat = cleaned_data.get("seat")
        if movie is not None and seat is not None and seat.movie_id != movie.pk:
            raise forms.ValidationError(
                "The selected seat does not belong to this movie."
            )
        return cleaned_data
