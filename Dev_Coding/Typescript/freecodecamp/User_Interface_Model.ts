// Made by: Hazzard
// FreeCodeCamp: TypeScript Course
// Project: Interface Modeling, Generics, and Union Types

export interface User {
  id: number;
  name: string;
  email: string;
  role: "admin" | "editor" | "viewer";
  isActive: boolean;
}

export interface ApiResponse<T> {
  status: "success" | "error";
  data?: T;
  errorMessage?: string;
}

export function formatUserInfo(user: User): string {
  return `User #${user.id}: ${user.name} (${user.email}) - Role: [${user.role.toUpperCase()}]`;
}

// Sample Usage
const sampleUser: User = {
  id: 101,
  name: "Alex Morgan",
  email: "alex@example.com",
  role: "admin",
  isActive: true
};

console.log(formatUserInfo(sampleUser));
