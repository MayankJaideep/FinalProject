/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Outfit', 'sans-serif'],
            },
            colors: {
                nyaya: {
                    dark: '#0A0A0B',
                    surface: '#121214',
                    border: '#27272A',
                    text: '#FAFAFA',
                    muted: '#A1A1AA',
                    primary: '#FFFFFF', // High contrast white for primary actions
                    accent: '#3B82F6', // Subtle blue accent
                }
            },
            boxShadow: {
                'glow': '0 0 40px -10px rgba(255, 255, 255, 0.1)',
                'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.3)',
            }
        },
    },
    plugins: [],
}
