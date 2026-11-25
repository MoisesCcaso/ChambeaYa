"""complete backend schema

Revision ID: 9f12c0a8d4e1
Revises: e48551cea8e6
Create Date: 2026-07-27
"""

from alembic import op
import sqlalchemy as sa


revision = "9f12c0a8d4e1"
down_revision = "e48551cea8e6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("convocatorias", schema=None) as batch_op:
        batch_op.add_column(sa.Column("beneficios", sa.Text(), nullable=True))

    op.create_table(
        "postulaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("convocatoria_id", sa.Integer(), nullable=False),
        sa.Column("practicante_id", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["convocatoria_id"], ["convocatorias.id"]),
        sa.ForeignKeyConstraint(["practicante_id"], ["practicantes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "convocatoria_id",
            "practicante_id",
            name="uq_postulacion_convocatoria_practicante",
        ),
    )

    with op.batch_alter_table("practicas", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            "uq_practicas_postulacion_id", ["postulacion_id"]
        )
        batch_op.create_foreign_key(
            "fk_practicas_postulacion_id",
            "postulaciones",
            ["postulacion_id"],
            ["id"],
        )

    op.create_table(
        "sugerencias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("practicante_id", sa.Integer(), nullable=False),
        sa.Column("convocatoria_id", sa.Integer(), nullable=False),
        sa.Column("puntaje_match", sa.Float(), nullable=False),
        sa.Column("habilidades_coincidentes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["convocatoria_id"], ["convocatorias.id"]),
        sa.ForeignKeyConstraint(["practicante_id"], ["practicantes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "practicante_id",
            "convocatoria_id",
            name="uq_sugerencia_practicante_convocatoria",
        ),
    )

    op.create_table(
        "notificaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_destino_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("leida", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_destino_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("notificaciones", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_notificaciones_leida"), ["leida"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_notificaciones_usuario_destino_id"),
            ["usuario_destino_id"],
            unique=False,
        )

    op.create_table(
        "certificados",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("practica_id", sa.Integer(), nullable=False),
        sa.Column("codigo_qr_valor", sa.String(length=80), nullable=True),
        sa.Column(
            "codigo_qr_url_verificacion", sa.String(length=255), nullable=True
        ),
        sa.Column("codigo_qr_hash", sa.String(length=64), nullable=True),
        sa.Column("documento_url", sa.String(length=255), nullable=True),
        sa.Column("documento_hash", sa.String(length=64), nullable=True),
        sa.Column("documento_contenido", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["practica_id"], ["practicas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo_qr_valor"),
        sa.UniqueConstraint("practica_id"),
    )


def downgrade():
    op.drop_table("certificados")

    with op.batch_alter_table("notificaciones", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_notificaciones_usuario_destino_id"))
        batch_op.drop_index(batch_op.f("ix_notificaciones_leida"))
    op.drop_table("notificaciones")
    op.drop_table("sugerencias")

    with op.batch_alter_table("practicas", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_practicas_postulacion_id", type_="foreignkey"
        )
        batch_op.drop_constraint(
            "uq_practicas_postulacion_id", type_="unique"
        )

    op.drop_table("postulaciones")

    with op.batch_alter_table("convocatorias", schema=None) as batch_op:
        batch_op.drop_column("beneficios")
