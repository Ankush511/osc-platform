import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { api, APIError } from '../api-client'

describe('API Client', () => {
  const originalFetch = global.fetch

  beforeEach(() => {
    global.fetch = vi.fn()
  })

  afterEach(() => {
    global.fetch = originalFetch
  })

  describe('apiRequest', () => {
    it('should make successful GET request', async () => {
      const mockData = { id: 1, name: 'Test' }
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
      } as Response)

      const result = await api.get('/test')

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
      expect(result).toEqual(mockData)
    })

    it('should include authorization header when token provided', async () => {
      const mockData = { success: true }
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
      } as Response)

      await api.get('/protected', 'test-token')

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/protected',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
          }),
        })
      )
    })

    it('should make POST request with data', async () => {
      const postData = { name: 'New Item' }
      const mockResponse = { id: 1, ...postData }
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      } as Response)

      const result = await api.post('/items', postData)

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/items',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
        })
      )
      expect(result).toEqual(mockResponse)
    })

    it('should handle 204 No Content response', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 204,
      } as Response)

      const result = await api.delete('/items/1')

      expect(result).toEqual({})
    })

    it('should throw APIError on failed request', async () => {
      const errorData = {
        message: 'Not found',
        error_code: 'NOT_FOUND',
      }
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => errorData,
      } as Response)

      try {
        await api.get('/not-found')
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error).toBeInstanceOf(APIError)
        expect((error as APIError).message).toBe('Not found')
      }
    })

    it('should handle network errors', async () => {
      vi.mocked(global.fetch).mockRejectedValueOnce(new Error('Network error'))

      try {
        await api.get('/test')
        expect.fail('Should have thrown an error')
      } catch (error) {
        expect(error).toBeInstanceOf(APIError)
        expect((error as APIError).message).toBe('Network error')
      }
    })

    it('should handle 401 unauthorized', async () => {
      const errorData = {
        message: 'Unauthorized',
        error_code: 'UNAUTHORIZED',
      }
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => errorData,
      } as Response)

      try {
        await api.get('/protected')
      } catch (error) {
        expect(error).toBeInstanceOf(APIError)
        expect((error as APIError).status).toBe(401)
      }
    })
  })

  describe('API methods', () => {
    it('should support PUT requests', async () => {
      const updateData = { name: 'Updated' }
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => updateData,
      } as Response)

      await api.put('/items/1', updateData)

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/items/1',
        expect.objectContaining({
          method: 'PUT',
        })
      )
    })

    it('should support PATCH requests', async () => {
      const patchData = { status: 'active' }
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => patchData,
      } as Response)

      await api.patch('/items/1', patchData)

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/items/1',
        expect.objectContaining({
          method: 'PATCH',
        })
      )
    })

    it('should support DELETE requests', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce({
        ok: true,
        status: 204,
      } as Response)

      await api.delete('/items/1')

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/items/1',
        expect.objectContaining({
          method: 'DELETE',
        })
      )
    })
  })
})
