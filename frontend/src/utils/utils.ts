import type { AxiosError } from "axios"

export const handleAxiosError = (error: AxiosError) => {
    if (error.response) {
        const data = error.response.data as { detail?: string };
        alert(`Ошибка ${error.response.status}: ${data.detail ?? JSON.stringify(error.response.data)}`)
    } else if (error.request) {
        alert('Ошибка: нет ответа от сервера')
    } else {
        alert(`Ошибка: ${error.message}`)
    }
}