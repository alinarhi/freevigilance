import { FrequencyTypeEnum, TaskStatusEnum, PVAStatusEnum, ActionEnum  } from "@/api-client";

export const FrequencyTypeDisplay: Record<FrequencyTypeEnum, string> = {
  [FrequencyTypeEnum.D]: "Ежедневно",
  [FrequencyTypeEnum.W]: "Каждую неделю",
  [FrequencyTypeEnum.M]: "Каждый месяц",
  [FrequencyTypeEnum.Y]: "Каждый год",
};

export const TaskStatusDisplay: Record<TaskStatusEnum, string> = {
  [TaskStatusEnum.NotStarted]: "Не начата",
  [TaskStatusEnum.InProgress]: "В работе",
  [TaskStatusEnum.Completed]: "Завершена",
  [TaskStatusEnum.Hidden]: "Скрыта",
};

export const PVAStatusDisplay: Record<PVAStatusEnum, string> = {
  [PVAStatusEnum.Active]: "Заключен",
  [PVAStatusEnum.Planned]: "Планируемый",
  [PVAStatusEnum.Ending]: "Завершающийся",
  [PVAStatusEnum.Completed]: "Завершен",
};

export const ActionDisplay: Record<ActionEnum, string> = {
  [ActionEnum.NUMBER_0]: "создал(-а)",
  [ActionEnum.NUMBER_1]: "изменил(-а)",
  [ActionEnum.NUMBER_2]: "удалил(-а)",
  [ActionEnum.NUMBER_3]: "получил(-а) доступ к",
};