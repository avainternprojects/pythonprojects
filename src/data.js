export const PRODUCTS = [
  {
    id: 'astronaut',
    name: 'Astronaut Helmet',
    category: 'Accessories',
    price: 299.99,
    rating: 4.7,
    reviewCount: 124,
    emoji: '🧑‍🚀',
    description: 'A detailed replica astronaut helmet perfect for display or cosplay. Features realistic visor reflection coating and adjustable interior padding.',
    specs: { 'Material': 'ABS Plastic + Polycarbonate', 'Weight': '1.2 kg', 'Dimensions': '30 × 28 × 35 cm', 'Color': 'White / Gold Visor', 'Warranty': '1 Year' },
    modelSrc: 'https://modelviewer.dev/shared-assets/models/glTF-Sample-Assets/Models/DamagedHelmet/glTF-Binary/DamagedHelmet.glb',
    iosSrc: '',
    image: 'https://modelviewer.dev/shared-assets/models/glTF-Sample-Assets/Models/DamagedHelmet/screenshot/screenshot-large.jpg'
  },
  {
    id: 'robot',
    name: 'Robot Companion',
    category: 'Electronics',
    price: 599.99,
    rating: 4.9,
    reviewCount: 287,
    emoji: '🤖',
    description: 'An AI-powered desktop robot companion with expressive movements and voice interaction. Responds to gestures and provides ambient lighting.',
    specs: { 'Connectivity': 'WiFi + Bluetooth 5.0', 'Battery': '4000mAh (8hr)', 'Sensors': 'Camera, Mic, ToF', 'Height': '22 cm', 'Warranty': '2 Years' },
    modelSrc: 'https://modelviewer.dev/shared-assets/models/RobotExpressive.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'horse',
    name: 'Decorative Horse Sculpture',
    category: 'Home Décor',
    price: 149.99,
    rating: 4.5,
    reviewCount: 89,
    emoji: '🐴',
    description: 'A stunning hand-crafted horse sculpture with metallic finish. An elegant centerpiece for any living room or office space.',
    specs: { 'Material': 'Resin + Metal Coating', 'Weight': '2.5 kg', 'Dimensions': '35 × 10 × 30 cm', 'Finish': 'Brushed Bronze', 'Warranty': '6 Months' },
    modelSrc: 'https://modelviewer.dev/shared-assets/models/Horse.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'chair',
    name: 'Sheen Office Chair',
    category: 'Furniture',
    price: 449.99,
    rating: 4.6,
    reviewCount: 203,
    emoji: '🪑',
    description: 'Ergonomic mesh office chair with lumbar support, adjustable armrests, and breathable fabric. Designed for all-day comfort during work.',
    specs: { 'Material': 'Mesh + Steel Frame', 'Max Weight': '120 kg', 'Adjustable Height': '42–52 cm', 'Armrests': 'Adjustable', 'Warranty': '5 Years' },
    modelSrc: 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/SheenChair/glTF-Binary/SheenChair.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'boom-box',
    name: 'Retro Boom Box Speaker',
    category: 'Electronics',
    price: 179.99,
    rating: 4.8,
    reviewCount: 342,
    emoji: '📻',
    description: 'Vintage-styled bluetooth speaker with modern audio tech. Delivers rich bass and 360° surround sound with a nostalgic retro aesthetic.',
    specs: { 'Output': '40W Stereo', 'Battery': '6000mAh (12hr)', 'Connectivity': 'BT 5.2 + AUX', 'Weight': '3.2 kg', 'Warranty': '2 Years' },
    modelSrc: 'https://modelviewer.dev/shared-assets/models/glTF-Sample-Assets/Models/BoomBox/glTF-Binary/BoomBox.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'lantern',
    name: 'Smart Ambient Lantern',
    category: 'Home Décor',
    price: 79.99,
    rating: 4.4,
    reviewCount: 156,
    emoji: '🏮',
    description: 'WiFi-enabled smart lantern with adjustable color temperature and brightness. Create the perfect ambiance with app-controlled lighting.',
    specs: { 'Lumens': '800 lm', 'Color Temp': '2700K–6500K', 'Control': 'App / Voice', 'Battery': '3000mAh', 'Warranty': '1 Year' },
    modelSrc: 'https://modelviewer.dev/shared-assets/models/glTF-Sample-Assets/Models/Lantern/glTF-Binary/Lantern.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'sofa',
    name: 'Cloud Comfort Sofa',
    category: 'Furniture',
    price: 1299.99,
    rating: 4.3,
    reviewCount: 67,
    emoji: '🛋️',
    description: 'Ultra-soft 3-seater sofa with memory foam cushions and stain-resistant fabric. Modular design allows flexible living room configurations.',
    specs: { 'Seating': '3-Seater', 'Material': 'Linen + Memory Foam', 'Dimensions': '210 × 90 × 85 cm', 'Weight': '45 kg', 'Warranty': '3 Years' },
    modelSrc: 'https://arlo.tools/models/sofa.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'headphones',
    name: 'ProSound ANC Headphones',
    category: 'Electronics',
    price: 349.99,
    rating: 4.8,
    reviewCount: 521,
    emoji: '🎧',
    description: 'Premium noise-cancelling headphones with spatial audio support. 40mm drivers deliver studio-quality sound with 30-hour battery life.',
    specs: { 'Driver': '40mm Dynamic', 'ANC': 'Hybrid Active', 'Battery': '30 Hours', 'Connectivity': 'BT 5.3 + USB-C', 'Warranty': '2 Years' },
    modelSrc: 'https://arlo.tools/models/Headphones.glb',
    iosSrc: '',
    image: ''
  }
];

export const REVIEWS_DATA = {
  'astronaut': [
    { user: 'SpaceFan42', rating: 5, date: '2026-06-15', text: 'Incredible detail! The visor coating looks amazing and the build quality is top-notch.' },
    { user: 'CosplayKing', rating: 4, date: '2026-06-10', text: 'Great for my costume collection. Slightly heavy but very comfortable to wear.' },
    { user: 'NASANerd', rating: 5, date: '2026-05-28', text: 'Best replica I have found at this price. The AR preview matched perfectly with what I received.' }
  ],
  'robot': [
    { user: 'TechLover99', rating: 5, date: '2026-06-20', text: 'This little robot has become my desk buddy. The AI responses are surprisingly smart!' },
    { user: 'GadgetGuru', rating: 5, date: '2026-06-12', text: 'Absolutely love the expressive movements. Kids are obsessed with it too.' },
    { user: 'MinimalDesk', rating: 4, date: '2026-06-01', text: 'Great design and functionality. Wish the battery lasted a bit longer.' }
  ],
  'horse': [
    { user: 'ArtCollector', rating: 5, date: '2026-06-18', text: 'Stunning piece. The bronze finish catches light beautifully. A real conversation starter.' },
    { user: 'HomeDesigner', rating: 4, date: '2026-06-05', text: 'Elegant and well-crafted. Slightly smaller than I expected but still gorgeous.' }
  ],
  'chair': [
    { user: 'RemoteWorker', rating: 5, date: '2026-06-22', text: 'Best office chair I have owned. My back pain is gone after switching to this.' },
    { user: 'GamerPro', rating: 4, date: '2026-06-14', text: 'Very comfortable for long gaming sessions. The mesh keeps you cool.' },
    { user: 'OfficeManager', rating: 5, date: '2026-05-30', text: 'Ordered 20 of these for our office. Everyone loves them.' }
  ],
  'boom-box': [
    { user: 'MusicHead', rating: 5, date: '2026-06-21', text: 'The sound quality is insane for a portable speaker. Bass hits hard!' },
    { user: 'RetroLover', rating: 5, date: '2026-06-16', text: 'Love the vintage look with modern tech inside. Turns heads everywhere.' },
    { user: 'PartyDJ', rating: 4, date: '2026-06-08', text: 'Great speaker for outdoor parties. Battery life is impressive.' }
  ],
  'lantern': [
    { user: 'CozyHome', rating: 4, date: '2026-06-19', text: 'Creates beautiful ambient light. The app control is convenient.' },
    { user: 'SmartHomeFan', rating: 5, date: '2026-06-11', text: 'Integrates perfectly with my smart home setup. Love the color options.' }
  ],
  'sofa': [
    { user: 'LivingRoomLove', rating: 4, date: '2026-06-17', text: 'Super comfortable and stylish. Delivery and setup were smooth.' },
    { user: 'FamilyOf4', rating: 5, date: '2026-06-09', text: 'Our whole family fits comfortably. The stain-resistant fabric is a lifesaver with kids.' }
  ],
  'headphones': [
    { user: 'Audiophile', rating: 5, date: '2026-06-23', text: 'Studio-quality sound with incredible noise cancellation. Worth every penny.' },
    { user: 'Commuter', rating: 5, date: '2026-06-15', text: 'Perfect for my daily commute. The ANC blocks out all subway noise.' },
    { user: 'PodcastFan', rating: 4, date: '2026-06-07', text: 'Crystal clear voice quality. Battery easily lasts my whole work week.' }
  ]
};

export const CATEGORIES = ['All', 'Electronics', 'Furniture', 'Home Décor', 'Accessories'];

export function getProduct(id) {
  return PRODUCTS.find(p => p.id === id);
}
