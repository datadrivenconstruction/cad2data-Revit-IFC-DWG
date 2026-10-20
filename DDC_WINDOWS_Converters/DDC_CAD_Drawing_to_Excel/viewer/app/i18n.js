// DDC Viewer UI texts (Russian / English).
(function (g) {
  'use strict';
  const T = {
    ru: {
      app: 'DDC Viewer', open: 'Открыть пакет', open_hint: 'Перетащите package.js или папку пакета сюда, или откройте файл',
      samples: 'Примеры', no_samples: 'Примеры не найдены', loading: 'Загрузка…', building: 'Построение геометрии…',
      model_tree: 'Модель', tab_spatial: 'Структура', tab_types: 'Категории', tab_layers: 'Слои', tab_views: 'Листы',
      search: 'Поиск по имени, типу, handle, GUID, свойству…', results: 'Найдено', properties: 'Свойства',
      nothing_selected: 'Выберите элемент в модели или в дереве', copy: 'Копировать', copied: 'Скопировано',
      copy_all: 'Копировать всё (JSON)', fit: 'Вписать (F)', ortho: 'Орто / перспектива (O)', walk: 'Обход от первого лица (P)',
      measure: 'Расстояние (M)', area: 'Площадь (A)', section: 'Секущая плоскость (C)', section_box: 'Секущий бокс (B)',
      hide: 'Скрыть (H)', isolate: 'Изолировать (I)', ghost: 'Полупрозрачно (G)', show_all: 'Показать всё (U)',
      colour_by: 'Цвет по свойству', colour_none: 'Исходные цвета', screenshot: 'Снимок экрана (Shift+S)',
      theme: 'Тема (T)', lang: 'Язык (L)', help: 'Горячие клавиши (?)', edges: 'Рёбра',
      coverage: 'Покрытие', coverage_title: 'Что декодировано и что нет', decoded: 'декодировано', refused: 'отказ',
      partial: 'частично', undrawn: 'Не отрисовано', approximations: 'Приближения', counts: 'Счётчики записей',
      not_in_model: 'Нет в модели', close: 'Закрыть', layers_all_on: 'Все вкл.', layers_all_off: 'Все выкл.',
      model_space: 'Модель', paper_space: 'Лист', viewport: 'Видовой экран', elements: 'элементов',
      units: 'Единицы', unresolved: 'не определены', axis: 'Ось', reverse: 'Развернуть', offset: 'Положение',
      sec_off: 'Выкл.', measure_hint: 'Щёлкните две точки. Esc — выход.', area_hint: 'Щёлкайте точки контура, Enter — завершить, Esc — выход.',
      walk_hint: 'WASD — движение, Q/E — вниз/вверх, Shift — быстрее, перетаскивание — обзор, Esc — выход.',
      distance: 'Расстояние', area_v: 'Площадь', perimeter: 'Периметр', clear: 'Очистить',
      cube_top: 'ВЕРХ', cube_bottom: 'НИЗ', cube_front: 'ПЕРЕД', cube_back: 'ЗАД', cube_left: 'ЛЕВО', cube_right: 'ПРАВО',
      format: 'Формат', source: 'Источник', producer: 'Создано', entities: 'Элементы', views: 'Виды',
      hk_title: 'Горячие клавиши', offline: 'Локально · без интернета', storey: 'Этаж', empty_tree: 'Нет данных',
      coverage_state: 'Состояние', truncated: 'Обрезано по бюджету', fps: 'кадр/с', selected: 'Выбрано',
      no_geometry: 'без геометрии', not_decoded: 'не декодировано', empty_view: 'Лист пуст: в пакете нет примитивов и видовых экранов для этого вида', legend: 'Легенда', geometry_missing: 'Геометрия не экспортирована',
    },
    en: {
      app: 'DDC Viewer', open: 'Open package', open_hint: 'Drop package.js or the package folder here, or open a file',
      samples: 'Samples', no_samples: 'No samples found', loading: 'Loading…', building: 'Building geometry…',
      model_tree: 'Model', tab_spatial: 'Spatial', tab_types: 'Categories', tab_layers: 'Layers', tab_views: 'Sheets',
      search: 'Search name, type, handle, GUID, property…', results: 'Found', properties: 'Properties',
      nothing_selected: 'Select an element in the model or the tree', copy: 'Copy', copied: 'Copied',
      copy_all: 'Copy all (JSON)', fit: 'Fit (F)', ortho: 'Ortho / perspective (O)', walk: 'First-person walk (P)',
      measure: 'Distance (M)', area: 'Area (A)', section: 'Section plane (C)', section_box: 'Section box (B)',
      hide: 'Hide (H)', isolate: 'Isolate (I)', ghost: 'Ghost (G)', show_all: 'Show all (U)',
      colour_by: 'Colour by property', colour_none: 'Original colours', screenshot: 'Screenshot (Shift+S)',
      theme: 'Theme (T)', lang: 'Language (L)', help: 'Keyboard shortcuts (?)', edges: 'Edges',
      coverage: 'Coverage', coverage_title: 'What was decoded and what was not', decoded: 'decoded', refused: 'refused',
      partial: 'partial', undrawn: 'Not drawn', approximations: 'Approximations', counts: 'Record counts',
      not_in_model: 'Not in model', close: 'Close', layers_all_on: 'All on', layers_all_off: 'All off',
      model_space: 'Model', paper_space: 'Sheet', viewport: 'Viewport', elements: 'elements',
      units: 'Units', unresolved: 'unresolved', axis: 'Axis', reverse: 'Flip', offset: 'Position',
      sec_off: 'Off', measure_hint: 'Click two points. Esc to exit.', area_hint: 'Click outline points, Enter to finish, Esc to exit.',
      walk_hint: 'WASD move, Q/E down/up, Shift faster, drag to look, Esc to exit.',
      distance: 'Distance', area_v: 'Area', perimeter: 'Perimeter', clear: 'Clear',
      cube_top: 'TOP', cube_bottom: 'BOTTOM', cube_front: 'FRONT', cube_back: 'BACK', cube_left: 'LEFT', cube_right: 'RIGHT',
      format: 'Format', source: 'Source', producer: 'Producer', entities: 'Elements', views: 'Views',
      hk_title: 'Keyboard shortcuts', offline: 'Local · offline', storey: 'Storey', empty_tree: 'No data',
      coverage_state: 'State', truncated: 'Truncated by budget', fps: 'fps', selected: 'Selected',
      no_geometry: 'no geometry', not_decoded: 'not decoded', empty_view: 'Empty sheet: the package has no primitives or viewports for this view', legend: 'Legend', geometry_missing: 'Geometry not exported',
    },
  };
  let lang = 'ru';
  try { lang = localStorage.getItem('ddcv.lang') || (navigator.language || 'ru').slice(0, 2); } catch (e) { /* storage blocked */ }
  if (!T[lang]) lang = 'en';
  const I18N = {
    get lang() { return lang; },
    set(l) { lang = T[l] ? l : 'en'; try { localStorage.setItem('ddcv.lang', lang); } catch (e) { /* ignore */ } },
    t(key) { return (T[lang] && T[lang][key]) || T.en[key] || key; },
  };
  (g.DDCV = g.DDCV || {}).i18n = I18N;
})(typeof window !== 'undefined' ? window : globalThis);
