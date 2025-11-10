<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.1.0
- Added mobile-first requirements for 日日鮮肉品專賣 meat store
- New principles: Mobile-First Design, Touch-Optimized UX
- Enhanced sections: Performance Requirements, User Experience Guidelines
- Added mobile-specific security and accessibility requirements
- Templates requiring updates: ✅ updated
- Follow-up TODOs: None
-->

# 日日鮮肉品專賣 Constitution

## Core Principles

### I. Security-First (NON-NEGOTIABLE)
Security MUST be implemented from day one, not retrofitted. All user data, payments, and personal information MUST be protected using industry-standard practices. Authentication and authorization MUST be implemented before any user-facing features. All inputs MUST be validated and sanitized. PCI DSS compliance considerations MUST guide payment handling design. Mobile security MUST include protection against mobile-specific threats (session hijacking, insecure storage, weak encryption).

**Rationale**: E-commerce platforms handle sensitive customer data, payment information, and financial transactions. Mobile users are particularly vulnerable to security threats due to varied network conditions and device capabilities.

### II. Mobile-First Design (NON-NEGOTIABLE)
ALL interfaces MUST be designed and implemented for mobile devices FIRST, then enhanced for larger screens. Touch targets MUST be minimum 44px (iOS) / 48px (Android). Navigation MUST be thumb-friendly with primary actions accessible via one-handed use. Responsive breakpoints MUST follow mobile-first approach: 320px → 768px → 1024px → 1440px. Mobile performance MUST be prioritized over desktop visual flourishes.

**Rationale**: 70%+ of e-commerce traffic comes from mobile devices in Taiwan. Mobile-first approach ensures optimal experience for the majority of users visiting the meat store.

### III. Touch-Optimized User Experience
All interactive elements MUST be designed for touch interaction. Hover states MUST have touch equivalents. Gesture support MUST include swipe navigation for product carousels and categories. Loading states MUST provide immediate feedback for slow 3G/4G connections. Form inputs MUST use appropriate mobile keyboards (numeric for phone, email for email, etc.).

**Rationale**: Touch interaction patterns differ significantly from mouse/keyboard. Meat store customers often shop while mobile, requiring intuitive touch-based interactions.

### IV. API-First Architecture
All business logic MUST be exposed through well-documented REST APIs before any UI implementation. APIs MUST follow consistent patterns, use proper HTTP status codes, and include comprehensive error handling. API contracts MUST be defined and tested independently of frontend implementations. Mobile APIs MUST support offline-first patterns with proper caching and sync strategies.

**Rationale**: Mobile users experience intermittent connectivity. API-first approach with offline support ensures customers can browse products and add to cart even with poor network conditions.

### V. Component-Driven UI Development
Frontend MUST be built using reusable, composable components with Tailwind CSS utility classes. Components MUST be documented with usage examples and prop interfaces. Design system consistency MUST be maintained through shared component library. Mobile components MUST include touch states and responsive variants. No custom CSS outside of Tailwind utilities without explicit justification.

**Rationale**: Component-driven development ensures UI consistency across mobile and desktop while reducing code duplication and improving maintainability for the meat store interface.

### VI. Test-Driven Development (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced. All critical user journeys (registration, login, checkout, payment) MUST have comprehensive integration tests on multiple device sizes. Mobile-specific tests MUST verify touch interactions, gesture support, and responsive layouts. API endpoints MUST have contract tests before implementation.

**Rationale**: Mobile e-commerce applications require high reliability across diverse devices and screen sizes. Touch interaction bugs directly impact meat store sales.

### VII. Performance & Scalability
Page load times MUST be under 2 seconds on 3G connections for mobile devices. First Contentful Paint (FCP) MUST be under 1.5 seconds. Largest Contentful Paint (LCP) MUST be under 2.5 seconds. Cumulative Layout Shift (CLS) MUST be under 0.1. Database queries MUST be optimized with proper indexing. Image optimization MUST use responsive images with WebP format support. Critical CSS MUST be inlined for above-the-fold content.

**Rationale**: Mobile performance directly impacts conversion rates. Studies show 53% of users abandon sites that take >3 seconds to load. Meat store product images require special optimization for mobile viewing.

## Mobile-Specific Requirements

### Responsive Design Standards
- **Breakpoints**: 320px (small mobile), 375px (standard mobile), 768px (tablet), 1024px (desktop), 1440px (large desktop)
- **Typography**: Minimum 16px base font size to prevent zoom on iOS
- **Touch Targets**: Minimum 44px tap targets with 8px spacing
- **Navigation**: Bottom tab bar or hamburger menu for mobile
- **Forms**: Single-column layout with large input fields
- **Product Images**: Optimized carousel with swipe support

### Mobile User Experience
- **One-Handed Use**: Primary actions accessible within thumb zone (bottom 1/3 of screen)
- **Gestures**: Swipe for product browsing, pull-to-refresh for inventory updates
- **Feedback**: Haptic feedback for successful actions (iOS)
- **Loading States**: Skeleton screens for content loading
- **Offline Support**: Basic browsing and cart functionality without network
- **Progressive Enhancement**: Core functionality works without JavaScript

### Mobile Performance
- **Bundle Size**: JavaScript bundles <50KB gzipped
- **Image Optimization**: WebP with JPEG fallback, responsive sizes
- **Lazy Loading**: Images and components below the fold
- **Caching Strategy**: Service Worker for static assets and API responses
- **Network Awareness**: Adaptive loading based on connection speed
- **Battery Efficiency**: Minimal background processing and animations

### Mobile Security
- **Secure Storage**: Sensitive data in iOS Keychain/Android Keystore
- **Network Security**: Certificate pinning for API communications  
- **Session Management**: Automatic logout on app backgrounding
- **Biometric Authentication**: Touch ID/Face ID support where available
- **Data Protection**: Encryption for local data storage
- **Privacy**: Location and camera permissions with clear justification

### Accessibility on Mobile
- **Screen Readers**: VoiceOver/TalkBack support for all interactive elements
- **Voice Navigation**: Voice Control compatibility on iOS
- **Dynamic Type**: Support for user text size preferences
- **Color Contrast**: 4.5:1 ratio minimum for normal text, 3:1 for large text
- **Focus Management**: Logical tab order for external keyboard users
- **Motion Sensitivity**: Respect prefers-reduced-motion settings

## Taiwan Market Mobile Considerations

### Local Mobile Usage Patterns
- **Primary Devices**: iPhone and Samsung Galaxy series dominance
- **Payment Methods**: Mobile payment integration (Apple Pay, Google Pay, Line Pay)
- **Social Integration**: Easy sharing to Line, Facebook, Instagram
- **Language Input**: Traditional Chinese input method support
- **Network Conditions**: 4G/5G coverage with occasional 3G fallback
- **Shopping Behavior**: Mobile research with cross-device purchase completion

### Meat Store Specific Mobile UX
- **Product Photography**: High-quality images with zoom capability for meat inspection
- **Freshness Indicators**: Clear expiration dates and quality badges
- **Quick Order**: Fast reorder for regular customers
- **Store Locator**: GPS-based nearest location finding
- **Inventory Alerts**: Push notifications for restocked premium items
- **Temperature Monitoring**: Cold chain information display

## Security Requirements

All authentication MUST use Django's built-in authentication with proper session management. Password policies MUST enforce strong passwords with complexity requirements. All forms MUST include CSRF protection. SQL injection protection MUST be ensured through Django ORM usage (no raw SQL without review). All file uploads MUST be validated and stored securely. Environment variables MUST be used for all secrets and configuration. Mobile apps MUST implement certificate pinning and secure local storage.

## Development Workflow

All features MUST follow the specification → clarification → planning → tasks → implementation workflow. Code reviews MUST verify security practices, test coverage, mobile responsiveness, and performance considerations. Database migrations MUST be reviewed for data integrity and rollback safety. Production deployments MUST include health checks and rollback procedures. Mobile testing MUST include real device testing on iOS and Android.

## Quality Assurance

### Mobile Testing Requirements
- **Device Testing**: Minimum iOS 14+ and Android 8+ support
- **Screen Size Testing**: 320px to 414px width coverage
- **Performance Testing**: Lighthouse mobile scores >90
- **Network Testing**: Slow 3G, Fast 3G, and offline scenarios
- **Touch Testing**: All interactive elements on physical devices
- **Cross-Browser**: Safari, Chrome, Samsung Internet testing

### Monitoring & Analytics
- **Core Web Vitals**: Continuous monitoring of LCP, FID, CLS
- **Real User Monitoring**: Performance data from actual mobile users
- **Error Tracking**: Mobile-specific error collection and alerting
- **Usage Analytics**: Mobile conversion funnel analysis
- **Performance Budget**: Fail builds that exceed mobile performance thresholds

## Governance

This constitution supersedes all other development practices and guidelines. All feature specifications, technical plans, and code reviews MUST verify compliance with these principles, especially mobile-first and performance requirements. Any violations MUST be justified with explicit documentation of risks and mitigation strategies. Amendments to this constitution require explicit approval and migration plan for existing code.

**Version**: 1.1.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-11-09 | **Mobile Update**: Added comprehensive mobile-first requirements for 日日鮮肉品專賣