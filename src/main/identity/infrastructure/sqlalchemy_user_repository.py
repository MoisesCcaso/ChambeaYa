from identity.domain.i_user_repository import IUserRepository
from identity.domain.expiring_token import ExpiringToken
from identity.domain.user import User
from shared.database import db
from identity.infrastructure.models.user_model import UserModel


class SqlAlchemyUserRepository(IUserRepository):
    def save(self, user):
        model = None
        if user.id is not None:
            model = db.session.get(UserModel, user.id)

        if model is None:
            model = UserModel()
            db.session.add(model)

        model.email = user.email
        model.password_hash = user.password_hash
        model.role = user.role
        model.status = user.status
        model.activation_token = user.activation_token
        model.activation_token_expires_at = user.activation_token_expires_at
        model.password_reset_token = user.password_reset_token
        model.password_reset_expires_at = user.password_reset_expires_at

        db.session.commit()
        return self._to_domain(model)

    def find_by_email(self, email):
        model = UserModel.query.filter_by(email=email).first()
        return self._to_domain(model)

    def find_by_id(self, user_id):
        model = db.session.get(UserModel, user_id)
        return self._to_domain(model)

    def find_by_activation_token(self, token):
        model = UserModel.query.filter_by(activation_token=token).first()
        return self._to_domain(model)

    def find_by_password_reset_token(self, token):
        model = UserModel.query.filter_by(password_reset_token=token).first()
        return self._to_domain(model)

    def _to_domain(self, model):
        if model is None:
            return None

        activation = None
        if model.activation_token or model.activation_token_expires_at:
            activation = ExpiringToken(
                model.activation_token, model.activation_token_expires_at
            )

        password_reset = None
        if model.password_reset_token or model.password_reset_expires_at:
            password_reset = ExpiringToken(
                model.password_reset_token, model.password_reset_expires_at
            )

        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=model.role,
            status=model.status,
            activation=activation,
            password_reset=password_reset,
        )
