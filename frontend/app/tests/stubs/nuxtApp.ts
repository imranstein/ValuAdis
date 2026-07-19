import { ref, type Ref, type UnwrapRef } from 'vue'

export const useRouter = () => ({
  push: async () => Promise.resolve(),
})

export const useState = <T>(_: string, init: (() => T) | T): Ref<UnwrapRef<T>> => {
  if (typeof init === 'function') {
    return ref((init as () => T)()) as Ref<UnwrapRef<T>>
  }
  return ref(init as T) as Ref<UnwrapRef<T>>
}

export const useRuntimeConfig = () => ({
  public: {
    apiBaseUrl: '',
  },
})
