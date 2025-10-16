# Frontend Architecture

## Overview

The Falcon Vision frontend is a modern React application built with TypeScript, providing an intuitive dashboard for monitoring person detection and analytics.

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Chakra UI
- **State Management**: TanStack Query (React Query)
- **Routing**: TanStack Router
- **HTTP Client**: Axios
- **Styling**: Emotion (CSS-in-JS)

## Project Structure

```
src/
├── components/     # Reusable UI components
├── routes/         # Page components and routing
├── client/         # API client (auto-generated)
├── hooks/          # Custom React hooks
├── utils/          # Utility functions
└── types/          # TypeScript type definitions
```

## Key Features

### Dashboard
- Real-time detection monitoring
- Analytics visualization
- User management interface
- Settings and configuration

### Authentication
- Login/logout functionality
- JWT token management
- Protected routes
- User session handling

### Real-time Updates
- WebSocket integration
- Live video streaming
- Detection notifications
- Status updates

## Component Architecture

### Layout Components
- **AppLayout**: Main application wrapper
- **Header**: Navigation and user menu
- **Sidebar**: Navigation menu
- **Footer**: Application footer

### Feature Components
- **DetectionDashboard**: Main detection interface
- **AnalyticsCharts**: Data visualization
- **UserManagement**: User administration
- **SettingsPanel**: Configuration options

## State Management

### TanStack Query
- Server state management
- Caching and synchronization
- Background updates
- Error handling

### Local State
- Component-level state with useState
- Form state with React Hook Form
- UI state management

## API Integration

### Auto-generated Client
- TypeScript client from OpenAPI spec
- Type-safe API calls
- Automatic request/response typing

### Error Handling
- Global error boundary
- API error handling
- User-friendly error messages

## Styling

### Chakra UI
- Component-based design system
- Responsive design
- Dark/light theme support
- Accessibility features

### Custom Styling
- Emotion for custom styles
- CSS-in-JS approach
- Theme customization
- Responsive breakpoints

## Performance

### Code Splitting
- Route-based code splitting
- Lazy loading
- Bundle optimization

### Caching
- API response caching
- Asset caching
- Browser caching strategies

## Development

### Development Tools
- Vite dev server
- Hot module replacement
- TypeScript compilation
- ESLint and Prettier

### Testing
- Playwright for E2E testing
- Component testing
- API testing
