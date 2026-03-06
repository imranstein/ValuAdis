// Ethiopian Property Seed Data
export const seedProperties = [
  {
    id: 1,
    title: "Modern Apartment in Bole",
    address: "Bole Medhanialem, Addis Ababa",
    type: "residential",
    subtype: "apartment",
    coordinates: [9.0116, 38.7616], // [latitude, longitude]
    price: 8500000, // ETB
    area: 120, // m²
    bedrooms: 2,
    bathrooms: 2,
    status: "available",
    yearBuilt: 2020,
    description: "Modern 2-bedroom apartment in prime Bole location",
    amenities: ["parking", "elevator", "security", "balcony"],
    images: ["/images/properties/bole-apartment-1.jpg"],
    listedDate: "2024-01-15",
    municipality: "Addis Ababa",
    subcity: "Bole"
  },
  {
    id: 2,
    title: "Villa in Kazanchis",
    address: "Kazanchis, Addis Ababa",
    type: "residential",
    subtype: "villa",
    coordinates: [9.0256, 38.7466],
    price: 15000000,
    area: 250,
    bedrooms: 4,
    bathrooms: 3,
    status: "available",
    yearBuilt: 2018,
    description: "Spacious 4-bedroom villa with garden",
    amenities: ["parking", "garden", "security", "garage"],
    images: ["/images/properties/kazanchis-villa-1.jpg"],
    listedDate: "2024-02-01",
    municipality: "Addis Ababa",
    subcity: "Kirkos"
  },
  {
    id: 3,
    title: "Office Space in Piassa",
    address: "Piassa, Addis Ababa",
    type: "commercial",
    subtype: "office",
    coordinates: [9.0346, 38.7426],
    price: 12000000,
    area: 180,
    bedrooms: 0,
    bathrooms: 2,
    status: "for_rent",
    yearBuilt: 2015,
    description: "Commercial office space in historic Piassa district",
    amenities: ["parking", "elevator", "security", "reception"],
    images: ["/images/properties/piassa-office-1.jpg"],
    listedDate: "2024-01-20",
    municipality: "Addis Ababa",
    subcity: "Arada"
  },
  {
    id: 4,
    title: "Shop in Mekelle",
    address: "Mekelle City Center, Mekelle",
    type: "commercial",
    subtype: "retail",
    coordinates: [13.4965, 39.4753],
    price: 7500000,
    area: 80,
    bedrooms: 0,
    bathrooms: 1,
    status: "available",
    yearBuilt: 2021,
    description: "Prime retail location in Mekelle city center",
    amenities: ["parking", "security", "storage"],
    images: ["/images/properties/mekelle-shop-1.jpg"],
    listedDate: "2024-02-10",
    municipality: "Mekelle",
    subcity: "Mekelle"
  },
  {
    id: 5,
    title: "Land in Bahir Dar",
    address: "Near Lake Tana, Bahir Dar",
    type: "land",
    subtype: "residential",
    coordinates: [11.5946, 37.3916],
    price: 5000000,
    area: 500,
    bedrooms: 0,
    bathrooms: 0,
    status: "available",
    yearBuilt: null,
    description: "Residential land with lake views",
    amenities: ["water", "electricity"],
    images: ["/images/properties/bahir-dar-land-1.jpg"],
    listedDate: "2024-01-25",
    municipality: "Bahir Dar",
    subcity: "Bahir Dar"
  },
  {
    id: 6,
    title: "Industrial Warehouse in Dire Dawa",
    address: "Industrial Zone, Dire Dawa",
    type: "industrial",
    subtype: "warehouse",
    coordinates: [9.6006, 41.8666],
    price: 20000000,
    area: 800,
    bedrooms: 0,
    bathrooms: 2,
    status: "available",
    yearBuilt: 2019,
    description: "Large industrial warehouse with loading docks",
    amenities: ["parking", "security", "loading_dock", "electricity"],
    images: ["/images/properties/dire-dawa-warehouse-1.jpg"],
    listedDate: "2024-02-05",
    municipality: "Dire Dawa",
    subcity: "Dire Dawa"
  },
  {
    id: 7,
    title: "Student Housing in Jimma",
    address: "Near Jimma University, Jimma",
    type: "residential",
    subtype: "student_housing",
    coordinates: [7.6666, 36.8336],
    price: 3500000,
    area: 60,
    bedrooms: 4,
    bathrooms: 2,
    status: "for_rent",
    yearBuilt: 2022,
    description: "Student housing near Jimma University",
    amenities: ["parking", "security", "wifi", "furnished"],
    images: ["/images/properties/jimma-student-1.jpg"],
    listedDate: "2024-02-15",
    municipality: "Jimma",
    subcity: "Jimma"
  },
  {
    id: 8,
    title: "Agricultural Land in Hawassa",
    address: "Hawassa Region, Hawassa",
    type: "agricultural",
    subtype: "farm",
    coordinates: [7.0556, 38.4756],
    price: 8000000,
    area: 2000,
    bedrooms: 0,
    bathrooms: 0,
    status: "available",
    yearBuilt: null,
    description: "Fertile agricultural land with water access",
    amenities: ["water", "electricity", "storage"],
    images: ["/images/properties/hawassa-farm-1.jpg"],
    listedDate: "2024-01-30",
    municipality: "Hawassa",
    subcity: "Hawassa"
  }
]

// Ethiopian regions and cities for map boundaries
export const ethiopianRegions = [
  {
    name: "Addis Ababa",
    coordinates: [9.0116, 38.7616],
    bounds: [[8.9, 38.6], [9.2, 39.0]]
  },
  {
    name: "Tigray",
    coordinates: [13.4965, 39.4753],
    bounds: [[12.5, 36.5], [14.5, 40.5]]
  },
  {
    name: "Amhara",
    coordinates: [11.5946, 37.3916],
    bounds: [[10.5, 35.5], [13.0, 39.5]]
  },
  {
    name: "Oromia",
    coordinates: [7.6666, 36.8336],
    bounds: [[5.0, 34.0], [10.0, 40.0]]
  },
  {
    name: "Somali",
    coordinates: [9.6006, 41.8666],
    bounds: [[4.0, 40.0], [11.0, 48.0]]
  },
  {
    name: "Southern Nations",
    coordinates: [7.0556, 38.4756],
    bounds: [[5.0, 35.0], [9.0, 40.0]]
  }
]

// Property type colors for map markers
export const propertyTypeColors = {
  residential: '#2E7D32', // Green
  commercial: '#1976D2', // Blue
  industrial: '#F57C00', // Orange
  agricultural: '#7B1FA2', // Purple
  land: '#616161' // Gray
}
