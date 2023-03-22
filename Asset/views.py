from django.shortcuts import render
import json
from django.http import HttpRequest, HttpResponse

from User.models import Entity,Department, User
from Asset.models import AssetClass, Asset, PendingRequests
from utils.utils_request import BAD_METHOD, request_failed, request_success, return_field
from utils.utils_require import MAX_CHAR_LENGTH, CheckRequire, require
from utils.utils_time import get_timestamp
# Create your views here.
