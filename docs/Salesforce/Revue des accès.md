# Revue des accès

# USERS
Champ FederationIdentifier :
- Renseigné → user fédéré via IdP (SSO/SAML)
- Vide → user local Salesforce

```
SELECT
  Id,
  Username,
  Name,
  Email,
  IsActive,
  UserType,
  Profile.Name,
  UserRole.Name,
  CreatedDate,
  LastLoginDate,
  LastPasswordChangeDate,
  PasswordExpirationDate,
  FederationIdentifier,
  NumberOfFailedLogins
FROM User
```

# PERMISSION SET

```
SELECT
  Id,
  AssigneeId,
  Assignee.Username,
  Assignee.Name,
  Assignee.Profile.Name,
  Assignee.UserRole.Name,
  Assignee.IsActive,
  Assignee.LastLoginDate,
  PermissionSetId,
  PermissionSet.Name,
  PermissionSet.IsOwnedByProfile,
  PermissionSetGroupId,
  IsActive,
  IsRevoked,
  ExpirationDate,
FROM PermissionSetAssignment
```
