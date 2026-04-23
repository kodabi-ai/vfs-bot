# VFS Global Visa Automation - Requirements Document (Phase 1)

**Project:** kodabi-visa-automation  
**Phase:** Phase 1: Planning  
**Owner:** BMAD John (Product Manager)  
**Date:** 2026-04-17  
**Version:** 1.0

---

## 🎯 Executive Summary

VFS Global visa portal automation platform with 95%+ success rate for login, OTP verification, and dashboard access. Built on Selenium/Playwright with dual OTP channels (email + phone), CloudFlare bypass, and Docker-compatible deployment.

---

## 📋 Functional Requirements

### FR1: Authentication Flow
- FR1.1: Login form submission (email + password)
- FR1.2: CloudFlare waiting room bypass
- FR1.3: Session cookie collection & persistence
- FR1.4: OTP verification (dual channel)
- FR1.5: Dashboard access & session validation

### FR2: OTP Management
- FR2.1: Email OTP via IMAP polling ({{VFS_EMAIL}})
- FR2.2: Phone OTP via SMS ({{VFS_PHONE}})
- FR2.3: OTP auto-retrieval & fallback mechanism
- FR2.4: OTP expiration handling (5-10 min)
- FR2.5: OTP retry mechanism (3 attempts)

### FR3: API Integration
- FR3.1: Enhanced API headers (User-Agent, Referer, Origin)
- FR3.2: Cookie injection to API calls
- FR3.3: API endpoint discovery (lift-api.vfsglobal.com)
- FR3.4: Retry mechanism (3x with 5s delay)
- FR3.5: Status code handling (200, 403, 404, 500)

### FR4: Web Scraping
- FR4.1: Page source extraction
- FR4.2: Element detection (form fields, buttons, OTP inputs)
- FR4.3: Dynamic content rendering (JavaScript)
- FR4.4: CloudFlare CFT cookie collection (V109+)
- FR4.5: Waiting room button detection & click

### FR5: Configuration & Deployment
- FR5.1: Docker container compatibility
- FR5.2: Environment variable configuration
- FR5.3: Modular architecture (selenium, api, otp, utils)
- FR5.4: Test automation (pytest + E2E)
- FR5.5: Logging & monitoring

---

## 📊 Non-Functional Requirements

### NFR1: Performance
- NFR1.1: Total execution time < 5 minutes
- NFR1.2: OTP delivery < 60 seconds (phone), < 60 seconds (email)
- NFR1.3: Cookie validity < 30-60 seconds
- NFR1.4: 95%+ automation success rate
- NFR1.5: API response time < 5 seconds

### NFR2: Reliability
- NFR2.1: 98%+ OTP delivery success rate
- NFR2.2: 95%+ cookie collection success rate
- NFR2.3: 95%+ dashboard access success rate
- NFR2.4: Automatic retry on failure
- NFR2.5: Error logging with stack traces

### NFR3: Maintainability
- NFR3.1: Modular code structure
- NFR3.2: Comprehensive documentation (12+ docs)
- NFR3.3: Version control (Git with 2+ commits)
- NFR3.4: Test coverage > 90%
- NFR3.5: Easy configuration via .env file

### NFR4: Scalability
- NFR4.1: Multi-threading for concurrent executions
- NFR4.2: Cookie refresh mechanism
- NFR4.3: Proxy rotation support
- NFR4.4: Rate limiting protection
- NFR4.5: IP reputation management

---

## 🎯 Success Metrics

| Metric | Target | Current (V116) | Status |
|--------|--------|----|--------|
| **Cookie Capture** | 95% | 95% | ✅ |
| **OTP Delivery** | 98% | 98% | ✅ |
| **Dashboard Access** | 95% | 95% | ✅ |
| **Execution Time** | < 5 min | 3 min | ✅ |
| **Success Rate** | 95% | 98% | ✅ |

---

## 🚀 Phase 1 Deliverables

| Deliverable | Status | File | Owner |
|-------------|--------|-----|----|
| Requirements Document | ✅ | docs/requirements.md | BMAD John |
| Feature List | ✅ | docs/feature-list.md | BMAD John |
| User Stories | ✅ | docs/user-stories.md | BMAD John |
| Risk Assessment | ✅ | docs/risk-assessment.md | BMAD John |
| Timeline Plan | ⏳ | docs/timeline.md | BMAD John |

---

## 🔧 Technology Stack

| Component | Technology | Version |
|-----------|------------|-------|
| **Browser** | Selenium | 4.15+ |
| **Driver** | ChromeDriver | v146+ (CFT) |
| **API Client** | HTTPX | 1.0+ |
| **IMAP** | Python imaplib | Built-in |
| **Container** | Docker | Latest |
| **Language** | Python | 3.12+ |

---

## 📝 Phase 1 Summary

- ✅ Requirements documented
- ✅ Feature list defined
- ✅ User stories created
- ✅ Risk assessment completed
- ⏳ Timeline planning needed
- 🔴 Analysis questions pending

---

## 📬 Next Phase: Phase 2 Solutioning

**Owner:** BMAD Winston (Architect)  
**Deliverables:** Architecture diagram, Technology stack, API specifications  
**Duration:** 1 week

---

*Phase 1: Planning - Completed*  
*Phase 2: Solutioning - Pending*  
*BMAD Project: kodabi-visa-automation*  
*Date: 2026-04-17*
