from rest_framework import status
from rest_framework.exceptions import APIException


class AlreadyBlocked(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'You have already blocked this user.'
    default_code = 'already_blocked'

class Is_Page(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'You are not a page'
    default_code = 'not_page'

class BlockNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "This user is not blocked."
    default_code = "block_not_found"