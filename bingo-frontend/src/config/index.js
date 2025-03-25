// bingo-frontend/src/config/index.js
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://caffeinated-divas.fly.dev'
  : 'http://localhost:8000';

const MEDIA_URL = process.env.NODE_ENV === 'production'
  ? 'https://caffeinated-divas.fly.dev/media'
  : 'http://localhost:8000/media';

// Use a reliable placeholder service
const PLACEHOLDER_IMAGE = 'https://placehold.co/150';

export default {
  API_BASE_URL,
  MEDIA_URL,
  PLACEHOLDER_IMAGE
};