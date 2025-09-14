export interface LearningBlock {
  id: number;
  topic: string;
  text_content: string;
  visualization_path: string | null;
}

export interface NotebookCell {
  cell_type: 'code' | 'markdown';
  source: string[];
  metadata: any;
}

export interface PlaygroundData {
  cells: NotebookCell[];
  metadata: any;
  nbformat: number;
  nbformat_minor: number;
}

export interface LearnResponse {
  learning_blocks: LearningBlock[];
  playground_path: string;
  main_topic: string;
  components: string[];
  timestamp: string;
}

export interface LearnRequest {
  topic: string;
  user_preferences: string;
}

export interface VideoPlayerProps {
  videoPath: string | null;
  title: string;
}
