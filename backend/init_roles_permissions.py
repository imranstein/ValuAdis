#!/usr/bin/env python3
"""
Initialize roles and permissions for ValuAdis platform
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.data.models import Role, Permission, User
from app.data.models.role import user_roles, role_permissions

def init_roles_permissions():
    """Initialize roles and permissions for the platform"""
    print(f"Connecting to database: {settings.DATABASE_URL}")
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Create permissions
        permissions_data = [
            # Property permissions
            {"name": "properties.create", "display_name": "Create Properties", "resource": "properties", "action": "create", "description": "Create new property records"},
            {"name": "properties.read", "display_name": "View Properties", "resource": "properties", "action": "read", "description": "View property details"},
            {"name": "properties.update", "display_name": "Update Properties", "resource": "properties", "action": "update", "description": "Update property information"},
            {"name": "properties.delete", "display_name": "Delete Properties", "resource": "properties", "action": "delete", "description": "Delete property records"},
            
            # Valuation permissions
            {"name": "valuations.create", "display_name": "Create Valuations", "resource": "valuations", "action": "create", "description": "Create property valuations"},
            {"name": "valuations.read", "display_name": "View Valuations", "resource": "valuations", "action": "read", "description": "View valuation details"},
            {"name": "valuations.update", "display_name": "Update Valuations", "resource": "valuations", "action": "update", "description": "Update valuation information"},
            {"name": "valuations.delete", "display_name": "Delete Valuations", "resource": "valuations", "action": "delete", "description": "Delete valuation records"},
            {"name": "valuations.approve", "display_name": "Approve Valuations", "resource": "valuations", "action": "approve", "description": "Approve valuation submissions"},
            
            # User management permissions
            {"name": "users.create", "display_name": "Create Users", "resource": "users", "action": "create", "description": "Create new user accounts"},
            {"name": "users.read", "display_name": "View Users", "resource": "users", "action": "read", "description": "View user information"},
            {"name": "users.update", "display_name": "Update Users", "resource": "users", "action": "update", "description": "Update user information"},
            {"name": "users.delete", "display_name": "Delete Users", "resource": "users", "action": "delete", "description": "Delete user accounts"},
            {"name": "users.assign_roles", "display_name": "Assign User Roles", "resource": "users", "action": "assign_roles", "description": "Assign roles to users"},
            
            # Reports permissions
            {"name": "reports.generate", "display_name": "Generate Reports", "resource": "reports", "action": "generate", "description": "Generate valuation and analytics reports"},
            {"name": "reports.export", "display_name": "Export Reports", "resource": "reports", "action": "export", "description": "Export reports to PDF/Excel"},
            
            # System administration permissions
            {"name": "system.admin", "display_name": "System Administration", "resource": "system", "action": "admin", "description": "Full system administration access"},
            {"name": "system.audit", "display_name": "System Audit", "resource": "system", "action": "audit", "description": "View system audit logs"},
            
            # Scraper permissions
            {"name": "scrapers.manage", "display_name": "Manage Scrapers", "resource": "scrapers", "action": "manage", "description": "Manage web scraper configurations"},
            {"name": "scrapers.run", "display_name": "Run Scrapers", "resource": "scrapers", "action": "run", "description": "Execute web scraper runs"},
        ]
        
        print("Creating permissions...")
        for perm_data in permissions_data:
            existing = db.query(Permission).filter_by(name=perm_data["name"]).first()
            if not existing:
                permission = Permission(**perm_data)
                db.add(permission)
        
        db.commit()
        print(f"Created {len(permissions_data)} permissions")
        
        # Create roles
        roles_data = [
            {
                "name": "valuer",
                "display_name": "Property Valuer",
                "description": "Basic property valuation role with limited permissions",
                "permissions": [
                    "properties.create", "properties.read", "properties.update",
                    "valuations.create", "valuations.read", "valuations.update",
                    "reports.generate", "reports.export"
                ]
            },
            {
                "name": "firm_admin",
                "display_name": "Firm Administrator",
                "description": "Firm-level administrator with user management capabilities",
                "permissions": [
                    "properties.create", "properties.read", "properties.update", "properties.delete",
                    "valuations.create", "valuations.read", "valuations.update", "valuations.delete", "valuations.approve",
                    "users.create", "users.read", "users.update", "users.assign_roles",
                    "reports.generate", "reports.export",
                    "scrapers.manage", "scrapers.run"
                ]
            },
            {
                "name": "municipal_admin",
                "display_name": "Municipal Administrator",
                "description": "Municipal-level administrator with oversight responsibilities",
                "permissions": [
                    "properties.read", "properties.update",
                    "valuations.read", "valuations.update", "valuations.approve",
                    "users.read", "users.update",
                    "reports.generate", "reports.export",
                    "system.audit"
                ]
            },
            {
                "name": "system_admin",
                "display_name": "System Administrator",
                "description": "Full system administrator with all permissions",
                "permissions": [perm["name"] for perm in permissions_data]
            }
        ]
        
        print("Creating roles...")
        for role_data in roles_data:
            existing = db.query(Role).filter_by(name=role_data["name"]).first()
            if not existing:
                role = Role(
                    name=role_data["name"],
                    display_name=role_data["display_name"],
                    description=role_data["description"]
                )
                db.add(role)
                db.flush()  # Get the role ID
                
                # Add permissions to role
                for perm_name in role_data["permissions"]:
                    permission = db.query(Permission).filter_by(name=perm_name).first()
                    if permission:
                        role.permissions.append(permission)
        
        db.commit()
        print(f"Created {len(roles_data)} roles")
        
        # Assign system admin role to first user if exists
        first_user = db.query(User).first()
        if first_user:
            system_admin_role = db.query(Role).filter_by(name="system_admin").first()
            if system_admin_role and system_admin_role not in first_user.roles:
                first_user.roles.append(system_admin_role)
                db.commit()
                print(f"Assigned system admin role to user: {first_user.email}")
        
        print("✅ Roles and permissions initialized successfully!")
        
        # Print summary
        total_roles = db.query(Role).count()
        total_permissions = db.query(Permission).count()
        print(f"\n📊 Summary:")
        print(f"   Total Roles: {total_roles}")
        print(f"   Total Permissions: {total_permissions}")
        
    except Exception as e:
        print(f"Error initializing roles and permissions: {e}")
        db.rollback()
    finally:
        db.close()
        engine.dispose()

if __name__ == "__main__":
    init_roles_permissions()
