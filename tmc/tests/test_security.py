from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestTmcSecurity(common.TransactionCase):
    # EPIC-015/TASK-005 — el orden de la escalera del privilegio GD debe ser
    # ESTRUCTURAL (Read Only -> User -> Manager por implicación), no producto del
    # desempate por id de res_groups.py (rank, sequence, id).
    #
    # Si esto se rompe, el widget de permisos (res_user_group_ids_field.js) borra
    # las opciones de MENOR nivel cuando una superior está implicada, y el dropdown
    # deja de ofrecer roles asignables. Fue el defecto de TASK-004 en ME y JUNCO:
    # ninguna suite lo vio, lo encontró una persona mirando un dropdown.
    #
    # NO relajar a "los 3 grupos están presentes": el bug NO era ausencia sino ORDEN.
    # El assert de ranks estrictamente crecientes es a propósito: falla también si
    # alguien "arregla" el orden con sequence en vez de la cadena de implicación.
    def test_privilege_ladder_order_is_structural(self):
        privilege = self.env.ref("tmc.res_groups_privilege_tmc")
        read_only = self.env.ref("tmc.group_read_only")
        user = self.env.ref("tmc.group_user")
        manager = self.env.ref("tmc.group_manager")

        hierarchy = self.env["res.groups"]._get_view_group_hierarchy()
        group_ids = hierarchy["privileges"][privilege.id]["group_ids"]
        self.assertEqual(
            group_ids,
            [read_only.id, user.id, manager.id],
            "la escalera GD debe ser Read Only -> User -> Manager",
        )

        ranks = [
            len(
                self.env["res.groups"].browse(gid).all_implied_ids & privilege.group_ids
            )
            for gid in group_ids
        ]
        self.assertEqual(
            ranks,
            [1, 2, 3],
            "el orden debe salir del rank (cadena real), no de sequence/id",
        )

    # Personal y Hidden Elements son MODIFICADORES, no roles: no deben entrar al
    # privilegio (el select excluyente los volvería incompatibles con User/Manager).
    def test_modifier_groups_have_no_privilege(self):
        for xmlid in ("tmc.group_personal", "tmc.group_hidden_elements"):
            self.assertFalse(
                self.env.ref(xmlid).privilege_id,
                f"{xmlid} es un modificador, no debe tener privilege_id",
            )
