export interface Member {
  name: string;
  color: string;
  avatar: string;
  points: number;
}

export interface Task {
  name: string;
  points: number;
  frequency: string;
  assignedMembers: Member[];
  completed: boolean;
}

export interface Reward {
  name: string;
  icon: string;
  pointsRequired: number;
  limit: number;
}

export interface Penalty {
  description: string;
  negativePoints: number;
}
