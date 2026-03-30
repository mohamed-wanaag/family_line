from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class FamilyPerson(models.Model):
    _name = 'family.person'
    _description = 'Family Member'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'full_name'
    _order = 'full_name asc'

    # ─── Basic Info ───────────────────────────────────────────────────────────
    full_name = fields.Char(
        string='Full Name',
        required=True,
        tracking=True,
    )
    date_of_birth = fields.Date(
        string='Date of Birth',
        tracking=True,
    )
    date_of_death = fields.Date(
        string='Date of Death',
        tracking=True,
    )
    status = fields.Selection(
        selection=[('alive', 'Alive'), ('deceased', 'Deceased')],
        string='Status',
        default='alive',
        required=True,
        tracking=True,
    )
    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string='Gender',
        required=True,
        tracking=True,
    )
    occupation = fields.Char(string='Occupation', tracking=True)
    education = fields.Char(string='Education', tracking=True)
    notes = fields.Text(string='Notes')
    image = fields.Binary(string='Photo', attachment=True)

    # ─── Computed Fields ──────────────────────────────────────────────────────
    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        store=False,
    )

    # ─── Hierarchy ────────────────────────────────────────────────────────────
    parent_id = fields.Many2one(
        comodel_name='family.person',
        string='Parent',
        ondelete='set null',
        index=True,
        tracking=True,
    )
    parent_ids = fields.Many2many(
        comodel_name='family.person',
        relation='family_person_parents_rel',
        column1='child_id',
        column2='parent_id',
        string='Parents',
        compute='_compute_parents',
    )
    child_ids = fields.One2many(
        comodel_name='family.person',
        inverse_name='parent_id',
        string='Children',
    )
    child_count = fields.Integer(
        string='Children Count',
        compute='_compute_child_count',
        store=True,
    )

  


    # ─── Computes ─────────────────────────────────────────────────────────────
    @api.depends('date_of_birth', 'date_of_death', 'status')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.date_of_birth:
                end = rec.date_of_death if rec.status == 'deceased' and rec.date_of_death else today
                delta = end - rec.date_of_birth
                rec.age = delta.days // 365
            else:
                rec.age = 0

    @api.depends('child_ids')
    def _compute_child_count(self):
        for rec in self:
            rec.child_count = len(rec.child_ids)

    @api.depends('parent_id')
    def _compute_parents(self):
        """Walk up hierarchy to collect all ancestors."""
        for rec in self:
            parents = self.env['family.person']
            current = rec.parent_id
            visited = set()
            while current and current.id not in visited:
                parents |= current
                visited.add(current.id)
                current = current.parent_id
            rec.parent_ids = parents

    @api.depends('event_ids')
    def _compute_event_count(self):
        for rec in self:
            rec.event_count = len(rec.event_ids)

    # ─── Constraints ──────────────────────────────────────────────────────────
    @api.constrains('parent_id')
    def _check_parent_no_cycle(self):
        """Prevent circular parent references."""
        for rec in self:
            current = rec.parent_id
            visited = set()
            while current:
                if current.id == rec.id:
                    raise ValidationError(
                        f"Circular hierarchy detected: '{rec.full_name}' cannot be its own ancestor."
                    )
                if current.id in visited:
                    break
                visited.add(current.id)
                current = current.parent_id

    @api.constrains('date_of_birth', 'date_of_death')
    def _check_death_after_birth(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_death:
                if rec.date_of_death < rec.date_of_birth:
                    raise ValidationError("Date of death cannot be before date of birth.")

    @api.constrains('status', 'date_of_death')
    def _check_deceased_has_date(self):
        for rec in self:
            if rec.status == 'deceased' and not rec.date_of_death:
                # Just a soft warning via chatter, not a hard block
                pass

    # ─── Onchange ─────────────────────────────────────────────────────────────
    @api.onchange('status')
    def _onchange_status(self):
        if self.status == 'alive':
            self.date_of_death = False

    # ─── Actions ──────────────────────────────────────────────────────────────
    def action_view_children(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f"Children of {self.full_name}",
            'res_model': 'family.person',
            'view_mode': 'tree,form',
            'domain': [('parent_id', '=', self.id)],
            'context': {'default_parent_id': self.id},
        }

    def action_view_events(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f"Events of {self.full_name}",
            'res_model': 'family.event',
            'view_mode': 'tree,form',
            'domain': [('person_id', '=', self.id)],
            'context': {'default_person_id': self.id},
        }

    def name_get(self):
        result = []
        for rec in self:
            name = rec.full_name
            if rec.date_of_birth:
                name += f" ({rec.date_of_birth.year})"
            result.append((rec.id, name))
        return result



    def get_org_chart_data(self):
        """This logic mimics hr.employee's org chart data provider"""
        self.ensure_one()
        
        # 1. Get Ancestors (Fathers/Grandfathers)
        # We limit to 1 or 2 levels for the display
        managers = []
        curr_parent = self.parent_id
        while curr_parent:
            managers.append({
                'id': curr_parent.id,
                'name': curr_parent.full_name,
                'title': curr_parent.occupation or 'Family Member',
                'direct_sub_count': curr_parent.child_count,
            })
            curr_parent = curr_parent.parent_id
            if len(managers) >= 3: break # Don't go too far up

        # 2. Get Siblings (Colleagues)
        colleagues = []
        if self.parent_id:
            colleagues = [{
                'id': p.id,
                'name': p.full_name,
                'title': p.occupation,
            } for p in self.parent_id.child_ids if p.id != self.id]

        # 3. Get Children (Subordinates)
        children = [{
            'id': c.id,
            'name': c.full_name,
            'title': c.occupation,
            'direct_sub_count': c.child_count,
        } for c in self.child_ids]

        return {
            'managers': managers,
            'managers_count': len(managers),
            'children': children,
            'self': {
                'id': self.id,
                'name': self.full_name,
                'title': self.occupation,
            },
            'colleagues': colleagues,
        }

    def action_open_lineage_chart(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Lineage of {self.full_name}',
            'res_model': 'family.person',
            'view_mode': 'hierarchy', # This is the magic key
            'domain': [('id', 'child_of', self.id)], # Shows this person and all descendants
            'context': {'default_parent_id': self.id},
        }