from app.security import MATRIX, Permission
def test_role_matrix_is_explicit():
    assert Permission.PROJECTS_DELETE in MATRIX['owner']
    assert Permission.PROJECTS_CREATE not in MATRIX['viewer']
    assert Permission.FEATURES_MANAGE not in MATRIX['member']
def test_no_authoritative_tenant_permission_in_roles():
    assert set(MATRIX) == {'owner','admin','member','viewer'}

