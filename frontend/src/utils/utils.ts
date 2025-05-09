import type { AxiosError } from "axios"

export const handleAxiosError = (error: AxiosError) => {
    if (error.response) {
        alert(`Ошибка ${error.response.status}: ${JSON.stringify(error.response.data)}`)
    } else if (error.request) {
        alert('Ошибка: нет ответа от сервера')
    } else {
        alert(`Ошибка: ${error.message}`)
    }
}