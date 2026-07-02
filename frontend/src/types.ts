export interface Product {
  id: number;
  code: string;
  title: string;
  price: number;
  description: string;
  is_available: boolean;
  images: { image: string }[];
  tags: { name: string }[];
  penalty?: number;
  uploaded_images?: string[];
}

export interface ProductSearchResult {
  code: string;
  title: string;
  description: string;
  is_available: boolean;
}

export interface CartItem {
  id: number;
  code: string;
  title: string;
  price: number;
  quantity: number;
  total: number;
  image?: string;
  penalty?: number;
}
