from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Follow
from .serializers import FollowSerializer


User = get_user_model()

class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        if target_user == request.user:
            return Response({"detail": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)
        follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
        if created:
            return Response({"detail": f"You are now following {target_user.username}"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Already following"}, status=status.HTTP_200_OK)

    def delete(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        follow = Follow.objects.filter(follower=request.user, following=target_user).first()
        if follow:
            follow.delete()
            return Response({"detail": f"You unfollowed {target_user.username}"}, status=status.HTTP_200_OK)
        return Response({"detail": "You are not following this user"}, status=status.HTTP_400_BAD_REQUEST)


class FollowersListView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Follow.objects.filter(following_id=user_id)


class FollowingListView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Follow.objects.filter(follower_id=user_id)
