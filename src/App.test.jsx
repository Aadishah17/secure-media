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
})

describe('App', () => {
  test('renders the upload workspace', () => {
    render(<App />)

    expect(screen.getByRole('heading', { name: /upload media/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/choose image/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze image/i })).toBeDisabled()
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
})
