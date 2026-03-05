class ApiService
{
  constructor ()
  {
    this.baseURL = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8020'
    this.defaultTimeout = 30000
    this.maxRetries = 3
    this.retryDelay = 1000
  }

  async request ( url, options = {} )
  {
    const {
      method = 'GET',
      headers = {},
      body = null,
      retries = this.maxRetries,
      timeout = this.defaultTimeout,
      credentials = 'omit'
    } = options

    const controller = new AbortController()
    const timeoutId = setTimeout( () => controller.abort(), timeout )

    try
    {
      const response = await fetch( `${ this.baseURL }${ url }`, {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: body ? JSON.stringify( body ) : null,
        credentials,
        signal: controller.signal
      } )

      clearTimeout( timeoutId )

      if ( !response.ok )
      {
        throw new Error( `HTTP ${ response.status }: ${ response.statusText }` )
      }

      return await response.json()
    } catch ( error )
    {
      clearTimeout( timeoutId )

      if ( error.name === 'AbortError' )
      {
        throw new Error( 'Request timeout' )
      }

      if ( retries > 0 && this.shouldRetry( error ) )
      {
        await this.delay( this.retryDelay * ( this.maxRetries - retries + 1 ) )
        return this.request( url, { ...options, retries: retries - 1 } )
      }

      throw error
    }
  }

  async get ( url, options = {} )
  {
    return this.request( url, { ...options, method: 'GET' } )
  }

  async post ( url, data, options = {} )
  {
    return this.request( url, { ...options, method: 'POST', body: data } )
  }

  async put ( url, data, options = {} )
  {
    return this.request( url, { ...options, method: 'PUT', body: data } )
  }

  async patch ( url, data, options = {} )
  {
    return this.request( url, { ...options, method: 'PATCH', body: data } )
  }

  async delete ( url, options = {} )
  {
    return this.request( url, { ...options, method: 'DELETE' } )
  }

  shouldRetry ( error )
  {
    // Retry on network errors and 5xx server errors
    return error.message.includes( 'fetch' ) ||
      error.message.includes( 'timeout' ) ||
      ( error.message.includes( 'HTTP 5' ) && !error.message.includes( 'HTTP 401' ) )
  }

  delay ( ms )
  {
    return new Promise( resolve => setTimeout( resolve, ms ) )
  }
}

export const apiService = new ApiService()
