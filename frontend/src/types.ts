// User roles
export enum UserRole {
  ADMIN = 'admin',
  ANNOTATOR = 'annotator',
}

// User status
export enum UserStatus {
  ACTIVE = 'active',
  WARNING = 'warning',
  BANNED = 'banned',
}

// Image review status
export enum ImageReviewStatus {
  NONE = 'none',
  PENDING = 'pending',
  REVIEWED = 'reviewed',
}

// Image task status
export enum ImageStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
}

// User type
export interface User {
  id: number;
  username: string;
  role: UserRole;
  status: UserStatus;
  balance_wallet: number;
}

// Image task type
export interface ImageTask {
  id: number;
  image_url: string;
  category_options: string;  // e.g. "Cat,Dog,Bird"
  options_list: string[];    // e.g. ["Cat", "Dog", "Bird"]
  final_label: string | null;
  review_status: ImageReviewStatus;
  bounty: number;
  assigned_count: number;
  status: ImageStatus;
}

// Annotation type
export interface Annotation {
  id: number;
  user: number;
  image: number;
  submitted_label: string;
  is_correct: boolean | null;
  payment: number | null;
  created_at: string;
}

// Payment type
export interface Payment {
  id: number;
  annotator: number;
  amount: number;
  payment_date: string;
}

// User stats type
export interface UserStats {
  accuracy: number;
  pendingBalance: number;
  totalAnnotated: number;
  correctCount: number;
}

// Unpaid user type
export interface UnpaidUser {
  userId: number;
  username: string;
  amount: number;
}