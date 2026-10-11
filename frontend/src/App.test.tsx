import {
    cleanup,
    fireEvent,
    render,
    screen,
    waitFor,
} from '@testing-library/react'
import {
    afterEach,
    beforeEach,
    describe,
    expect,
    it,
    vi,
} from 'vitest'
import App from './App'

const analytics = {
    total_predictions: 0,
    predicted_failures: 0,
    predicted_normal: 0,
    average_failure_probability: 0,
    risk_distribution: [],
    recent_predictions: [],
}

const prediction = {
    id: 1,
    model_name: 'TestModel',
    failure_probability: 0.12,
    decision_threshold: 0.35,
    predicted_failure: 0,
    status: 'No failure predicted',
    risk_level: 'Low',
    created_at: '2026-10-11T12:00:00.000Z',
}

const history = {
    count: 0,
    predictions: [],
}

beforeEach(() => {
    vi.stubGlobal(
        'fetch',
        vi.fn(async (input: RequestInfo | URL) => {
            const url = String(input)

            // Match the singular prediction endpoint first.
            if (url === '/api/predict' || url.endsWith('/api/predict')) {
                return new Response(JSON.stringify(prediction), {
                    status: 200,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })
            }

            if (url.includes('/api/analytics/summary')) {
                return new Response(JSON.stringify(analytics), {
                    status: 200,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })
            }

            if (url.includes('/api/predictions')) {
                return new Response(JSON.stringify(history), {
                    status: 200,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })
            }

            return new Response(
                JSON.stringify({ detail: 'Not found' }),
                {
                    status: 404,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                },
            )
        }),
    )
})

afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
})

describe('Industrial AI dashboard', () => {
    it('renders the main dashboard', async () => {
        render(<App />)

        expect(
            screen.getByRole('heading', {
                name: /machine health overview/i,
            }),
        ).toBeInTheDocument()

        expect(
            screen.getByRole('button', {
                name: /run failure prediction/i,
            }),
        ).toBeInTheDocument()

        expect(
            await screen.findByText('Total predictions'),
        ).toBeInTheDocument()
    })


    it('submits sensor readings and displays the prediction', async () => {
        render(<App />)

        const button = screen.getByRole('button', {
            name: /run failure prediction/i,
        })

        const form = button.closest('form')

        expect(form).not.toBeNull()

        // Trigger React's form submit handler directly.
        fireEvent.submit(form!)

        await waitFor(() => {
        expect(vi.mocked(fetch).mock.calls.some(
            ([input]) => String(input) === '/api/predict'
        )).toBe(true)
        })


        expect(
            await screen.findByText((_, element) =>
                element?.tagName.toLowerCase() === 'strong' &&
                element.textContent?.trim() === 'No failure predicted'
            )
        ).toBeInTheDocument()

        expect(screen.getByText('12.0', { exact: true })).toBeInTheDocument()
    })

})
