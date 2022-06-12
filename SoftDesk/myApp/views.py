from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .models import Projects, Users, Issues, Comments, Contributors
from .serializers import ProjectSerializer, CustomUserSerializer, IssueSerializer, CommentSerializer, \
    ContributorSerializer, ProjectWithIdSerializer
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import HasProjectPermission, HasContributorPermission, HasIssuePermission, HasCommentPermission
from django.shortcuts import get_object_or_404


class UserRegistrationViewset(ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer
    queryset = Users.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create_user(email=request.data['email'],
                                   last_name=request.data['last_name'],
                                   password=request.data['password'],
                                   first_name=request.data['first_name'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ProjectsView(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):

        print(request.user)
        qs = Projects.objects.all()
        serializer = ProjectSerializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save(author_user=request.user)
            contributor = Contributors.objects.create(project=project,
                                                      user=request.user,
                                                      role='Author')
            contributor.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ProjectViewSet(ModelViewSet):
    model = Projects
    permission_classes = [IsAuthenticated, HasProjectPermission]
    serializer_class = ProjectSerializer
    lookup_field = 'project_id'
    queryset = Projects.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = Projects.objects.get(id=kwargs['id'])
        if Projects.objects.get(id=kwargs['id']):
            raw = Projects.objects.get(id=kwargs['id'])
            project = ProjectWithIdSerializer(raw, many=False)
            return Response(project.data,
                            status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        obj = get_object_or_404(Projects, id=kwargs['id'])
        self.check_object_permissions(self.request, obj)
        instance = Projects.objects.get(id=kwargs['id'])
        serializer = ProjectWithIdSerializer(instance,
                                             data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        destruct = get_object_or_404(Projects, id=kwargs['id'])
        self.check_object_permissions(self.request, destruct)
        instance = kwargs['id']
        project_destroyed = Projects.objects.filter(id=instance)
        self.perform_destroy(project_destroyed)
        message = 'You deleted the project' + str(instance)
        return Response({'message': message},
                        status=status.HTTP_204_NO_CONTENT)


class ContributorsView(ModelViewSet):
    permission_classes = [IsAuthenticated, HasContributorPermission]
    queryset = Contributors.objects.all()
    serializer_class = ContributorSerializer

    def list(self, request, *args, **kwargs):

        instances = Contributors.objects.filter(project=kwargs['id'])
        serializer = ContributorSerializer(instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):

        serializer = ContributorSerializer(data=request.data)
        instances = Contributors.objects.filter(project=kwargs['id'])

        instance = Projects.objects.get(id=kwargs['id'])
        user_contributor = Users.objects.get(pk=request.data['user'])

        if instances.filter(user=user_contributor):
            message = 'This user is already a contributor of this project'

        else:
            if serializer.is_valid():
                serializer.save(project=instance, user=user_contributor, role='Contributor')
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_200_OK)

        return Response({'message': message},
                        status=status.HTTP_204_NO_CONTENT)


class ContributorsDeletionView(ModelViewSet):
    queryset = Contributors.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, HasContributorPermission]

    def destroy(self, request, *args, **kwargs):
        project_instance = Projects.objects.get(id=kwargs['id'])

        user_instance = Users.objects.filter(pk=kwargs['user_id'])[0]
        # user_instance = Users.objects.get(id=kwargs['user_id'])
        print(Users.objects.get(pk=kwargs['user_id']))
        Contrib_deleted = Contributors.objects.filter(project=project_instance).filter(user=user_instance)
        print(Contrib_deleted)
        self.check_object_permissions(self.request, Contrib_deleted)
        self.perform_destroy(Contrib_deleted)
        message = 'The contributor is  deleted'
        return Response({'message': message}, status=status.HTTP_204_NO_CONTENT)


class IssuesView(ModelViewSet):
    permission_classes = [IsAuthenticated, HasIssuePermission]
    serializer_class = IssueSerializer
    queryset = Issues.objects.all()

    def list(self, request, *args, **kwargs):
        instance = Projects.objects.get(id=kwargs['id'])
        qs = []
        for elem in Issues.objects.all():
            if elem.project == instance:
                qs.append(elem)
        serializer = IssueSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        project = Projects.objects.get(id=kwargs['id'])
        serializer = IssueSerializer(data=request.data)
        assignee = Users.objects.get(id=request.data['assignee_user'])
        if Contributors.objects.filter(user=assignee).filter(project=project).exists():
            if serializer.is_valid():
                serializer.save(author_user=request.user, project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors)
        else:
            message = 'The assignee user is not yet a contributor to this project'
            return Response({'message': message}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        issue = Issues.objects.get(id=kwargs['issue_id'])
        self.check_object_permissions(request, issue)

        serializer = IssueSerializer(issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if Issues.objects.filter(id=kwargs['issue_id']).exists():

            issue = Issues.objects.get(id=kwargs['issue_id'])
            self.check_object_permissions(request, issue)
            self.perform_destroy(issue)
            message = 'The issue was successfully deleted'
            return Response({'message': message}, status=status.HTTP_204_NO_CONTENT)
        else:
            message = 'This issue doesnt exists'
            return Response({'message': message}, status=status.HTTP_204_NO_CONTENT)


class CommentsView(ModelViewSet):
    permission_classes = [IsAuthenticated, HasCommentPermission]
    serializer_class = CommentSerializer
    queryset = Comments.objects.all()

    def list(self, request, *args, **kwargs):
        instance = Issues.objects.get(id=kwargs['issue_id'])
        qs = []
        for elem in Comments.objects.all():
            if elem.issue == instance:
                qs.append(elem)
        serializer = CommentSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        issue = Issues.objects.get(id=kwargs['issue_id'])
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(issue=issue, author_user_id=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class SoloCommentView(ModelViewSet):
    permission_classes = [IsAuthenticated, HasCommentPermission]
    serializer_class = CommentSerializer
    queryset = Comments.objects.all()

    def retrieve(self, request, *args, **kwargs):
        if Comments.objects.get(id=kwargs['comment_id']):
            comment = Comments.objects.get(id=kwargs['comment_id'])
            serializer = CommentSerializer(comment, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        comment = Comments.objects.get(id=kwargs['comment_id'])
        self.check_object_permissions(request, comment)
        serializer = CommentSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = kwargs['comment_id']
        comment = Comments.objects.get(id=instance)
        self.check_object_permissions(request, comment)
        self.perform_destroy(comment)
        message = 'The comment is deleted'
        return Response({'message': message}, status=status.HTTP_204_NO_CONTENT)
