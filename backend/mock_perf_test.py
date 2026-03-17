import time
from unittest.mock import MagicMock

# Simulate database objects
class MockRole:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.display_name = name
        self.description = name

class MockUser:
    def __init__(self, id):
        self.id = id
        self.email = f"user{id}@test.com"
        self.full_name = "User"
        self.phone = "123"
        self.municipality = "Mun"
        self.license_number = "123"
        self.is_active = True
        self.is_verified = True
        self.is_admin = False
        self.is_valuer = True
        self.created_at = "2023-01-01"
        self.updated_at = "2023-01-01"
        self.roles = [MockRole(1, "role1")]

def test_original_n_plus_one(num_users):
    users = [MockUser(i) for i in range(num_users)]

    # Mock db.query
    query_calls = 0
    def mock_query(*args):
        nonlocal query_calls
        query_calls += 1
        mock = MagicMock()
        mock.join.return_value.filter.return_value.all.return_value = [MockRole(1, "role1")]
        return mock

    db = MagicMock()
    db.query = mock_query

    start_time = time.time()

    user_responses = []
    for user in users:
        user_role_objs = db.query(MockRole).join(MagicMock()).filter(MagicMock()).all()
        # Simulating UserResponse construction (omitted for brevity in mock)
        user_responses.append({
            "id": user.id,
            "roles": [{"id": r.id} for r in user_role_objs]
        })

    end_time = time.time()
    return query_calls, (end_time - start_time) * 1000

def test_optimized_selectinload(num_users):
    users = [MockUser(i) for i in range(num_users)]

    # In selectinload, the query is done once by SQLAlchemy
    # So we don't query inside the loop
    query_calls = 0  # 1 main query + 1 selectinload query in reality, but loop has 0

    start_time = time.time()

    user_responses = []
    for user in users:
        # accessing user.roles which was eagerly loaded
        user_role_objs = user.roles
        user_responses.append({
            "id": user.id,
            "roles": [{"id": r.id} for r in user_role_objs]
        })

    end_time = time.time()
    return query_calls, (end_time - start_time) * 1000

print(f"{'Method':<20} | {'Users':<10} | {'DB Queries':<12} | {'Time (ms)':<10}")
print("-" * 60)

for count in [10, 100, 1000]:
    q_orig, t_orig = test_original_n_plus_one(count)
    q_opt, t_opt = test_optimized_selectinload(count)

    # Real DB query count for orig is N + 1 (1 for users, N for roles)
    # For opt, it's 1 + 1 (1 for users, 1 for selectinload roles)
    print(f"{'Original (N+1)':<20} | {count:<10} | {q_orig + 1:<12} | {t_orig:.2f}")
    print(f"{'Optimized':<20} | {count:<10} | {2:<12} | {t_opt:.2f}")
