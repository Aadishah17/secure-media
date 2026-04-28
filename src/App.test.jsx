import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeAll, describe, expect, test, vi } from 'vitest'
import App from './App.jsx'

beforeAll(() => {
  URL.createObjectURL = vi.fn(() => 'blob:preview')
  URL.revokeObjectURL = vi.fn()
})

afterEach(() => {
  vi.clearAllMocks()
  delete global.fetch
})

describe('App', () => {
  test('renders the upload workspace', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: /upload media/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/choose image/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze image/i })).toBeDisabled()
    expect(screen.getByText('Awaiting upload')).toHaveClass('text-slate-700')
  })

  test('accepts an image file and clears the selection', async () => {
    const user = userEvent.setup()
    const image = new File(['image-data'], 'claim-photo.png', { type: 'image/png' })

    render(<App />)
    await user.upload(screen.getByLabelText(/choose image/i), image)

    expect(screen.getByText('claim-photo.png')).toBeInTheDocument()
    expect(screen.getByAltText(/preview of claim-photo\.png/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze image/i })).toBeEnabled()

    await user.click(screen.getByRole('button', { name: /clear selection/i }))

    expect(screen.queryByText('claim-photo.png')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze image/i })).toBeDisabled()
  })

  test('shows loading state and renders upload results', async () => {
    const user = userEvent.setup()
    const image = new File(['image-data'], 'claim-photo.png', { type: 'image/png' })
    let resolveRequest
    global.fetch = vi.fn(
      () =>
        new Promise((resolve) => {
          resolveRequest = resolve
        })
    )

    render(<App />)
    await user.upload(screen.getByLabelText(/choose image/i), image)
    await user.click(screen.getByRole('button', { name: /analyze image/i }))

    expect(screen.getByText(/uploading image/i)).toBeInTheDocument()

    resolveRequest({
      ok: true,
      json: async () => ({
        similarity: 97.5,
        duplicate: true,
        owner: 'Aadishah',
        blockchain_verified: true
      })
    })

    expect(await screen.findByText('97.5%')).toBeInTheDocument()
    expect(screen.getByText(/duplicate detected/i)).toBeInTheDocument()
    expect(screen.getByText('Aadishah')).toBeInTheDocument()
    expect(screen.getAllByText(/verified/i)).toHaveLength(2)
  })

  test('rejects non-image file selection', async () => {
    const user = userEvent.setup({ applyAccept: false })
    const textFile = new File(['plain text'], 'notes.txt', { type: 'text/plain' })

    render(<App />)
    await user.upload(screen.getByLabelText(/choose image/i), textFile)

    expect(screen.getByText(/upload an image file to continue/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze image/i })).toBeDisabled()
  })

  test('shows text fallback when backend error response is not json', async () => {
    const user = userEvent.setup()
    const image = new File(['image-data'], 'claim-photo.png', { type: 'image/png' })

    global.fetch = vi.fn(async () => ({
      ok: false,
      clone: () => ({
        text: async () => 'Server exploded'
      }),
      json: async () => {
        throw new Error('Unexpected token <')
      }
    }))

    render(<App />)
    await user.upload(screen.getByLabelText(/choose image/i), image)
    await user.click(screen.getByRole('button', { name: /analyze image/i }))

    expect(await screen.findByText('Server exploded')).toBeInTheDocument()
  })
})
