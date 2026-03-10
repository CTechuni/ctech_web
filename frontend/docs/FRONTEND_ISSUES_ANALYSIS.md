# 🔍 Frontend Issues & Audit Report

**Status**: ⏳ Analysis Complete, Remediation Pending  
**Created**: 2024  
**Scope**: CTech Frontend (Astro + Vanilla JS)

---

## 📋 Executive Summary

Frontend audit completed. **12 critical issues** identified across:
- Authentication utilities (`src/utils/auth.js`)
- API configuration (`src/config/api.js`)
- Form components (`LoginForm.astro`, `SignupForm.astro`)
- Admin components (multiple)

**Risk Level**: 🔴 **HIGH** - Storage inconsistency, debug outputs, missing validations

---

## 🚨 CRITICAL ISSUES

### 1. ⚠️ INCONSISTENT TOKEN STORAGE (CRITICAL)

**Severity**: 🔴 **CRITICAL**

**Problem**:
- `AuthManager` uses **sessionStorage** for tokens
- `authenticatedRequest()` in `api.js` uses **localStorage**
- This causes authentication to fail unexpectedly

**Locations**:
- ✗ `src/utils/auth.js:15` - `getToken()` uses `sessionStorage.getItem('authToken')`
- ✗ `src/utils/auth.js:25` - `setAuthData()` uses `sessionStorage.setItem()`
- ✗ `src/config/api.js:73` - `authenticatedRequest()` uses `localStorage.getItem('authToken')`

**Impact**:
- API requests fail because token not found in localStorage
- Sessions may not persist across page reloads (if sessionStorage intended)
- Security inconsistency across auth system

**Solution**: Standardize to ONE storage mechanism:
- **Option A** (Recommended): Use `sessionStorage` (more secure, clears on browser close)
- **Option B**: Use `localStorage` (persistent across sessions)

---

### 2. ⚠️ DEBUG CONSOLE.LOG STATEMENTS (SECURITY RISK)

**Severity**: 🔴 **CRITICAL**

**Problem**: Multiple debug statements leak sensitive information to console

**Locations**:
```javascript
// src/utils/auth.js - Lines 64, 68, 69, 78, 88
console.log(`DEBUG AUTH: Sending POST to ${url} with email: ${email}`); // Line 64
console.error('DEBUG AUTH: Login failed status:', response.status);      // Line 68
console.error('DEBUG AUTH: error details:', err);                        // Line 69
console.log('DEBUG AUTH: Login success, data:', data);                   // Line 78
console.error('DEBUG AUTH: Fetch error or logic error:', error);         // Line 88

// src/pages/components/LoginForm.astro - Lines 334, 342, 352
console.log(`DEBUG LOGIN: Attempting login for ${email}...`);            // Line 334
console.log('DEBUG LOGIN: Success!', result);                            // Line 342
console.log(`DEBUG LOGIN: Role is "${role}"...`);                        // Line 352
console.log('Actualizando UI para usuario:', user);                      // Line 361

// src/pages/components/SignupForm.astro - Line 408
console.log('Registro exitoso:', result);                                // Line 408
```

**Impact**:
- Exposes user emails, roles, passwords hashes in browser console
- Violates GDPR/privacy regulations
- Helpful for attackers to understand flow

**Solution**: Remove ALL `console.log()` and `console.error()` statements
- Keep error logging server-side only
- Use specialized logging library if needed (e.g., LogRocket)

---

### 3. ⚠️ INCORRECT API ENDPOINTS (ROUTING ERROR)

**Severity**: 🔴 **CRITICAL**

**Problem**: API endpoints in `config/api.js` don't match backend routes

**Locations** (`src/config/api.js`):
```javascript
// INCORRECT - Backend uses /users/ not /auth/register
AUTH.REGISTER: '/auth/register'  // Should be: '/users/'

// INCORRECT - Backend doesn't have /user/ prefix
USER: {
    PROFILE: '/user/profile',      // Should be: '/users/{id}' or '/users/me'
    UPDATE_PROFILE: '/user/profile', // Should be: '/users/{id}'
    CHANGE_PASSWORD: '/user/change-password', // Not implemented in backend
    DELETE_ACCOUNT: '/user/delete'   // Should be: '/users/{id}'
}
```

**Backend Reality**:
- Registration: **POST /users/** (not /auth/register)
- Get user: **GET /users/{id}**
- Update user: **PUT /users/{id}**
- Delete user: **DELETE /users/{id}**

**Impact**:
- Signup flow completely broken (calls wrong endpoint)
- User profile operations fail silently
- 404 errors in console

**Solution**: Update endpoints to match backend catalog

---

### 4. ⚠️ AUTHMANAGER INSTANTIATION INCONSISTENCY

**Severity**: 🟠 **HIGH**

**Problem**: Components create new instances instead of using global `authManager`

**Locations**:
```javascript
// WRONG - Creates new instance
// AdminUsersSection.astro
import { AuthManager } from '../../utils/auth';
const auth = new AuthManager();
await auth.get('users'); // ❌ Method doesn't exist!

// AdminMentorsSection.astro
import { AuthManager } from '../../utils/auth';
const auth = new AuthManager();
await auth.get('users'); // ❌ Method doesn't exist!

// SignupForm.astro - Dynamic import
const mod = await import('../../utils/auth.js');
const authManager = mod.authManager ?? mod.default ?? null; // ⚠️ Fallback logic
```

**Issue**: `AuthManager` doesn't have `.get()` method - would fail at runtime

**Solution**:
- Import the singleton: `import { authManager } from '../../utils/auth.js'`
- Use: `authManager.fetch('/endpoint')` instead of `auth.get()`

---

### 5. ⚠️ TOKEN EXPIRATION NOT HANDLED

**Severity**: 🟠 **HIGH**

**Problem**: No automatic token refresh or expiration check during requests

**Current Flow**:
1. User logs in → token stored (30 min expiration)
2. After 29 minutes → token still appears valid in `isAuthenticated()`
3. At minute 31 → API call fails with 401
4. User sees error, must login again

**Missing**:
- No refresh token mechanism
- No proactive expiration check before API calls
- No redirect to login with "Session expired" message

**Solution**:
- Implement refresh token endpoint (POST /auth/refresh)
- Check token exp before API calls
- Auto-refresh 5 min before expiration
- Clear session on 401 response

---

### 6. ⚠️ INCOMPLETE ERROR PARSING

**Severity**: 🟠 **HIGH**

**Problem**: Error handling differs between implementations

**auth.js** (Lines 68-70):
```javascript
const err = await response.json().catch(() => ({}));
// Handles both Array and String detail:
const detail = Array.isArray(err.detail)
    ? err.detail.map(e => e.msg).join(', ')
    : (err.detail || 'Credenciales inválidas');
```

**api.js** (Lines 79-80):
```javascript
// Only handles string, no Array handling
const error = await response.json().catch(() => ({ message: 'Error desconocido' }));
throw new Error(error.message || `Error ${response.status}`);
```

**Forms** (LoginForm, SignupForm):
- Use raw `error.message` without parsing detail

**Impact**: Form validation errors (which come as Array) are not properly displayed

**Solution**: Standardize error parsing across all files

---

### 7. ⚠️ REGISTER METHOD INCOMPLETE

**Severity**: 🟠 **HIGH**

**Location**: `src/utils/auth.js:88`

**Problem**:
```javascript
async register(userData) {
    // Sends userData directly, no validation
    return AuthManager.fetch('/users/', {
        method: 'POST',
        body: JSON.stringify(userData)
    });
}
```

**Issues**:
- Doesn't validate userData schema matches backend expectations
- Doesn't handle password hashing (frontend shouldn't but should validate strength)
- No error differentiation (user exists, invalid email, etc.)
- `userData` contains plain password - security concern

**Backend Expects**:
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str  # Will be hashed
    name_user: str
    role: Optional[str] = "user"
```

**SignupForm sends**:
```javascript
{
    community: "...",
    inviteCode: "...",
    fullName: "...",
    email: "...",
    password: "...",
    terms: true
}
```

**Mismatch**: `fullName` vs `name_user`, extra fields like `community`, `inviteCode`

---

### 8. ⚠️ EMAIL VALIDATION TOO SIMPLE

**Severity**: 🟠 **MEDIUM**

**Location**: `SignupForm.astro:382`

**Problem**:
```javascript
if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
    // Too simple regex
}
```

**Issues**:
- Accepts invalid emails like `test@.com`, `@test.com`
- Doesn't validate against disposable emails
- Backend uses `EmailStr` which is stricter

**Better Regex**:
```javascript
/^[^\s@]+@[^\s@]+\.[^\s@]+$/ // Better but still not perfect
// Or use backend validation (better approach)
```

---

### 9. ⚠️ NO SESSION RECOVERY AFTER 401

**Severity**: 🟠 **MEDIUM**

**Problem**: When token expires (401), user is redirected to `/` without context

**Current** (`AuthManager.fetch()` Lines 120-125):
```javascript
if (response.status === 401) {
    sessionStorage.removeItem('authToken');
    sessionStorage.removeItem('user');
    window.location.href = '/';  // ❌ Loses context
    return;
}
```

**Issues**:
- User doesn't know why they were logged out
- Users lose their current context/form data
- No way to redirect back after login

**Solution**:
- Store intended URL before redirect
- Show "Session expired" message
- Redirect back to original page after login

---

### 10. ⚠️ INCONSISTENT LOGIN ERROR MESSAGES

**Severity**: 🟡 **MEDIUM**

**Problem**: Error handling differs between signup and login

**LoginForm** (Line 342):
```javascript
// Shows same error for all failures
passwordError.textContent = error.message || 'Credenciales incorrectas';
```

**SignupForm** (Lines 377-387):
```javascript
// Shows specific errors per field
if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
    showError('email_signup', 'emailSignupError', 'Correo inválido');
}
if (password.length < 8) {
    showError('password_signup', 'passwordSignupError', 'Min. 8 caracteres');
}
```

**Impact**: Poor UX consistency

---

### 11. ⚠️ LOGOUT FLOW SUBOPTIMAL

**Severity**: 🟡 **MEDIUM**

**Locations**:
- `auth.js:104` - Only clears storage and redirects
- `LoginForm.astro:365` - Calls logout then reloads page (redundant)

**Current**:
```javascript
// auth.js
logout() {
    this.clearAuthData();
    window.location.href = '/';  // ❌ Only does this
}

// LoginForm.astro
window.logout = async function () {
    await authManager.logout();
    alert('Sesión cerrada');
    window.location.reload();  // ❌ Redundant
};
```

**Issues**:
- No server-side token revocation (if implemented)
- Alert dialog unnecessary
- reload() after navigate is redundant

---

### 12. ⚠️ TOKEN_TYPE NOT VALIDATED

**Severity**: 🟡 **LOW**

**Problem**: Backend returns `token_type: "bearer"` but frontend doesn't validate

**Backend Response** (from `auth/login`):
```json
{
    "access_token": "eyJ...",
    "token_type": "bearer",
    "user": {...}
}
```

**Frontend** (`auth.js:80`):
```javascript
this.setAuthData(data.access_token, data.user);
// ❌ Ignores data.token_type, doesn't validate it's "bearer"
```

**Solution**: Validate `token_type === "bearer"` before storing

---

## 📊 Issue Summary Table

| # | Issue | Severity | Type | Fix Time |
|---|-------|----------|------|----------|
| 1 | Storage Inconsistency | 🔴 CRITICAL | Architecture | 15 min |
| 2 | Debug Logs | 🔴 CRITICAL | Security | 10 min |
| 3 | Wrong Endpoints | 🔴 CRITICAL | Routing | 10 min |
| 4 | AuthManager Instantiation | 🟠 HIGH | Logic | 20 min |
| 5 | Token Expiration | 🟠 HIGH | Security | 30 min |
| 6 | Error Parsing | 🟠 HIGH | Logic | 15 min |
| 7 | Register Incomplete | 🟠 HIGH | Logic | 20 min |
| 8 | Email Validation | 🟠 MEDIUM | Validation | 10 min |
| 9 | 401 Recovery | 🟠 MEDIUM | UX | 20 min |
| 10 | Login Error UI | 🟡 MEDIUM | UX | 15 min |
| 11 | Logout Flow | 🟡 MEDIUM | Logic | 10 min |
| 12 | Token Type | 🟡 LOW | Validation | 5 min |

**Total Estimated Fix Time**: ~180 minutes (~3 hours)

---

## ✅ Recommended Fix Order

1. **Phase 1 (CRITICAL)** - Fix Breaking Issues:
   - Remove debug console.log statements (10 min)
   - Fix API endpoints (10 min)
   - Standardize storage (sessionStorage) (15 min)
   
2. **Phase 2 (HIGH)** - Fix Auth Logic:
   - Fix AuthManager instantiation patterns (20 min)
   - Fix register method schema (20 min)
   - Standardize error parsing (15 min)
   
3. **Phase 3 (MEDIUM)** - Improve Security:
   - Add token refresh mechanism (30 min)
   - Add 401 recovery (20 min)
   - Add token_type validation (5 min)
   
4. **Phase 4 (POLISH)** - UI/UX:
   - Improve email validation (10 min)
   - Standardize error messages (15 min)
   - Improve logout flow (10 min)

---

## 📝 Notes

- **User Input Needed**: Should frontend use `sessionStorage` or `localStorage`?
- **Related Backend**: Issues tie to backend improvements already completed
- **Testing**: All changes require testing against actual backend
- **Documentation**: Will create updated FRONTEND_INTEGRATION.md after fixes

---

## 🔗 Related Files

- Backend Issues: [AUDIT_SUMMARY.md](../backend/AUDIT_SUMMARY.md)
- Frontend Config: [src/config/api.js](src/config/api.js)
- Auth Utility: [src/utils/auth.js](src/utils/auth.js)
- Forms: `src/pages/components/LoginForm.astro`, `SignupForm.astro`
- Admin Pages: `src/pages/admin/`
