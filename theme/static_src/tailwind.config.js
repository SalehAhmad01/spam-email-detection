module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../apps/**/templates/**/*.html',
        '../../**/templates/**/*.html',
    ],
    theme: {
        extend: {
            colors: {
                slate: {
                    850: '#0f172a',
                    950: '#020617',
                },
                guard: {
                    navy: '#0f172a',
                    slate: '#1e293b',
                    blue: '#1d4ed8',
                    accent: '#2563eb',
                    subtle: '#64748b',
                }
            }
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
