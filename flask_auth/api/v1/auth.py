import logging
from http import HTTPStatus as HTTP

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_current_user, get_jwt, jwt_required

from flask_auth.services.utils import role_required
from services.models_serv import AuthServ, UserServ
from services.utils import check_user_agent, throttling_user_agent

auth = Blueprint('auth', __name__)


@auth.route('/user_crud', methods=['POST', 'PUT'])
@jwt_required(optional=True)
@throttling_user_agent()
def user_crud():
    """
    ---
    post:
      description: Creates a user in the database.(email, password fields). Identification is by name, a mandatory field. Authentication is not needed.
      summary: create_user
      requestBody:
        content:
          application/json:
            schema: CreateUserSchema
      responses:
        201:
          description: User created. Login is email
        400:
          description: password != password2 or length < 8  // Wrong email or password or name
        403:
          description: FORBIDDEN
        422:
          description: UNPROCESSABLE ENTITY
      tags:
        - Auth
    put:
      description: Changes the user data. Authentication is required.
      summary: change_user (need access token)
      security:
        - jwt_key: []
      requestBody:
        content:
          'application/json':
            schema: PutUserSchema
      responses:
        202:
          description: User update
        400:
          description: password != password2 or length < 8  // Wrong email or password or name
        401:
          description: UNAUTHORIZED
        403:
          description: FORBIDDEN
      tags:
        - Auth
    """
    response = UserServ.user_crud()
    return response


@auth.route("/login", methods=["POST"])
@throttling_user_agent()
def login():
    """
    ---
    post:
      summary: Returns a pair (REFRESH/ACCESS)
      description: Accepts a login (email)/password and returns a pair (REFRESH/ACCESS) of tokens. Logs the authorization.
      requestBody:
        description: Login and password
        content:
          application/json:
            schema: LoginInputSchema
      responses:
        200:
          description: Receiving result (REFRESH/ACCESS)
          content:
            application/json:
              schema: OutputSchema
        400:
          description: Error
          content:
            application/json:
              schema: ErrorSchema
        403:
          description: FORBIDDEN
      tags:
        - Auth
    """
    json = request.get_json()
    if 'email' not in json or 'password' not in json:
        return jsonify("Not email or password"), HTTP.BAD_REQUEST
    user: UserServ = UserServ.query.filter_by(email=json['email']).scalar()
    if not user or not user.check_password(json['password'], json['email']):
        return jsonify("Wrong email or password"), HTTP.UNAUTHORIZED
    access_token, refresh_token = AuthServ.login_refresh_service(user, True)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
@check_user_agent()
def logout():
    """
    ---
    delete:
      summary: Logout (need access/refresh token)
      description: Accepts any valid (ACCESS/REFRESH) token and revokes all (ACCESS/REFRESH) keys - putting them on the redis blocklist
      responses:
        200:
          description: Access/Refresh tokens revoked
        422:
          description: UNPROCESSABLE ENTITY
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    AuthServ.logout_service(get_current_user())
    return jsonify('All tokens revoked'), HTTP.OK


@auth.route("/logout_all", methods=["DELETE"])
@jwt_required(verify_type=False)
@check_user_agent()
def logout_all():
    """
    ---
    delete:
      summary: Logout all (need access/refresh token)
      description: Accepts any valid (ACCESS/REFRESH) token and revokes all (ACCESS/REFRESH) keys of all user_agents - putting them on redis blocklist
      responses:
        200:
          description: All Access/Refresh tokens revoked
        422:
          description: UNPROCESSABLE ENTITY
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    AuthServ.logout_all_service(get_current_user())
    return jsonify('All tokens revoked'), HTTP.OK


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@check_user_agent()
def refresh():
    """
    ---
    post:
      summary: Refreshes (REFRESH/ACCESS) pair (need access/refresh token)
      responses:
        200:
          description: Result of getting updated (REFRESH/ACCESS)
          content:
            application/json:
              schema: OutputSchema
        401:
          description: Error
          content:
            application/json:
              schema: ErrorSchema
        401:
          description: Expired authorization token (REFRESH)
          content:
            application/json:
              schema: ErrorSchema
        422:
          description: Invalid authorization header (REFRESH)
          content:
            application/json:
              schema: ErrorSchema
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    user = get_current_user()
    access_token, refresh_token = AuthServ.login_refresh_service(user)
    return jsonify(access_token=access_token, refresh_token=refresh_token), HTTP.CREATED


@auth.route("/history_auth", methods=["GET"])
@jwt_required()
@throttling_user_agent()
def history_auth():
    """
    ---
    get:
      summary: History_auth (need access token)
      description: Returns a list of all authorizations of the user. Access token required.
      parameters:
        - name: page
          in: query
          description: Page number
          required: false
          schema:
            type: integer
        - name: size
          in: query
          description: Page size
          required: false
          schema:
            type: integer
      responses:
        200:
          description: Authorization History.
          content:
            application/json:
              schema: HistoryAuthSchema
        401:
          description: UNAUTHORIZED
        422:
          description: UNPROCESSABLE ENTITY
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    jwt_dict = get_jwt()
    page = int(request.args.get('page', default=0))
    size = int(request.args.get('size', default=5))
    history = AuthServ.history_auth(jwt_dict['sub'], page, size)
    return jsonify(history_auth=history)


@auth.route("/check_user", methods=["GET"])
@jwt_required()
def check_user():
    """
    ---
    get:
      summary: check_user (need access token)
      description: Handler for microservices, checks validity of access key. Access token required.
      responses:
        200:
          description: OK
        401:
          description: UNAUTHORIZED
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    logging.error('INFO USER_AGENT_PLATFORM - %s', request.user_agent)
    return jsonify(), HTTP.OK


@auth.route("/check_user_is_subscriber", methods=["GET"])
@jwt_required()
@role_required('subscriber')
def check_user_is_subscriber():
    """
    ---
    get:
      summary: check_user (need access token)
      description: Handler for microservices, checks validity of access key and whether the owner is a subscriber. Access token required.
      responses:
        200:
          description: OK.
        401:
          description: UNAUTHORIZED
        403:
          description: FORBIDDEN
      security:
        - jwt_key: []
      tags:
        - Auth
    """
    return jsonify(), HTTP.OK


@auth.route("/get_user_by_id", methods=["GET"])
def get_user_by_id():
    """
    ---
    get:
      summary: get_user
      description: Handler for microservices
      parameters:
        - name: id
          in: query
          description: user ID
          required: true
          schema:
            type: string
      responses:
        200:
          description: OK.
          content:
            application/json:
              schema: GetByIDUserSchema
        404:
          description: NOT_FOUND
      tags:
        - Auth
    """
    id = request.args.get('id')
    user = UserServ.get_obj_by_id(id)
    if not user:
        return jsonify(), HTTP.NOT_FOUND
    return jsonify(user_id=user.id, username=user.name, email=user.email), HTTP.OK
