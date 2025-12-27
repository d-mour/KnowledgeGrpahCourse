import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import yaml
from .output.csv_writer import CSVWriter
from .html_cache import HtmlCache

class Parser:
    def __init__(self, config):
        self.config = config
        self.variables = self._extract_variables()
        self.rulesets = self._extract_rulesets()
        self.tasks = self._extract_tasks()
        self.cache = HtmlCache()

    def _extract_variables(self):
        """Извлекает переменные из конфигурации"""
        variables = {}
        for item in self.config:
            if 'value' in item and 'id' in item:
                variables[item['id']] = item['value']
        return variables

    def _extract_rulesets(self):
        return {rs['id']: rs for rs in self.config if 'rules' in rs and 'id' in rs}

    def _extract_tasks(self):
        return [task for task in self.config if 'url' in task]

    def run(self):
        print(f"Loaded {len(self.variables)} variables, {len(self.rulesets)} rulesets and {len(self.tasks)} tasks")
        
        if not self.tasks:
            print("No tasks found in configuration")
            return
        
        for task in self.tasks:
            print(f"Processing task: {task['name']}")
            self._process_task(task)

    def _process_task(self, task):
        html = self.cache.get_page(task['url'])
        soup = BeautifulSoup(html, 'html.parser')
        
        print(f"DEBUG: Starting pre_pattern search: {task['pre_pattern']}")
        
        
        containers = self._find_pre_pattern(soup, task['pre_pattern'])
        if not containers:
            print(f"DEBUG: Container not found with pattern: {task['pre_pattern']}")
            print(f"DEBUG: Trying alternative search methods...")
            
            
            fallback_container = self._find_container_alternative(soup, task.get('pre_pattern_fallback'))
            if fallback_container:
                containers = [fallback_container]
                print(f"DEBUG: Found container using fallback pattern")
            else:
                
                self._debug_dom_structure(soup, task['pre_pattern'])
                raise ValueError(f"Container not found with pattern: {task['pre_pattern']}")

        print(f"DEBUG: Found {len(containers)} container(s)")
        rules = self._resolve_rules(task['rules'])
        
        
        limit = task.get('limit')
        include_headers = task.get('include_headers', False)
        row_selector = task.get('row_selector', 'tr')  
        
        
        all_data = []
        for i, container in enumerate(containers):
            print(f"Processing container {i+1}/{len(containers)}")
            print(f"DEBUG: Container type: {type(container)}, tag: {getattr(container, 'name', 'N/A')}")
            print(f"DEBUG: Container content preview: {str(container)[:200]}...")
            
            container_data = self._parse_container(container, rules, task.get('setnull', True), 
                                                 base_url=task['url'], limit=limit, 
                                                 include_headers=include_headers,
                                                 row_selector=row_selector)
            all_data.extend(container_data)
        
        output_dir = 'parsed_csv'
        os.makedirs(output_dir, exist_ok=True)
        csv_path = os.path.join(output_dir, task['csv_file'])
        
        CSVWriter.write(all_data, csv_path, [r['name'] for r in rules])
        print(f"Saved {len(all_data)} records from {len(containers)} containers to {csv_path}")

    def _find_pre_pattern(self, soup, pattern):
        """Улучшенный метод поиска контейнеров с поддержкой диапазонов"""
        if not pattern:
            return None
            
        try:
            current = soup
            parts = pattern.split('/')
            print(f"DEBUG: Processing pre_pattern parts: {parts}")
            
            for i, part in enumerate(parts):
                if part == '':
                    print(f"DEBUG: Part {i}: empty, skipping")
                    continue
                    
                print(f"DEBUG: Part {i}: '{part}'")
                print(f"DEBUG: Current element: {getattr(current, 'name', type(current))}")
                
                
                current = self._process_pre_pattern_part(current, part, i)
                if current is None:
                    print(f"DEBUG: Part {i} '{part}' returned None")
                    return None
                else:
                    print(f"DEBUG: Part {i} '{part}' successful")
                    if isinstance(current, list):
                        print(f"DEBUG: Found {len(current)} elements")
                    else:
                        print(f"DEBUG: Element: {getattr(current, 'name', type(current))}")
                    
            
            if isinstance(current, list):
                print(f"DEBUG: Returning {len(current)} containers")
                return current
            
            else:
                print(f"DEBUG: Returning 1 container")
                return [current]
                
        except Exception as e:
            print(f"DEBUG: Error in pre_pattern processing: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _process_pre_pattern_part(self, element, part, part_index):
        """Обрабатывает одну часть pre_pattern с поддержкой классов и диапазонов"""
        print(f"DEBUG: Processing part {part_index}: '{part}'")
        
        
        range_class_match = re.match(r'([\w-]+)\.([\w-]+):\[(\d+)-(\d+)\]', part)
        if range_class_match:
            tag = range_class_match.group(1)
            class_name = range_class_match.group(2)
            start_idx = int(range_class_match.group(3))
            end_idx = int(range_class_match.group(4))
            print(f"DEBUG: Range selector with class: {tag}.{class_name}[{start_idx}-{end_idx}]")
            elements = element.find_all(tag, class_=class_name)
            print(f"DEBUG: Found {len(elements)} {tag} elements with class '{class_name}' for range [{start_idx}-{end_idx}]")
            result = []
            for idx in range(start_idx, end_idx + 1):
                if idx < len(elements):
                    result.append(elements[idx])
            print(f"DEBUG: Returning {len(result)} elements from range")
            return result
        
        
        single_class_match = re.match(r'([\w-]+)\.([\w-]+):\[(\d+)\]', part)
        if single_class_match:
            tag = single_class_match.group(1)
            class_name = single_class_match.group(2)
            idx = int(single_class_match.group(3))
            print(f"DEBUG: Single index selector with class: {tag}.{class_name}[{idx}]")
            elements = element.find_all(tag, class_=class_name)
            print(f"DEBUG: Found {len(elements)} {tag} elements with class '{class_name}'")
            if len(elements) > idx:
                return elements[idx]
            print(f"DEBUG: Index {idx} out of range for {tag}.{class_name} (max: {len(elements)-1})")
            return None
        
        
        range_match = re.match(r'([\w-]+):\[(\d+)-(\d+)\]', part)
        if range_match:
            tag = range_match.group(1)
            start_idx = int(range_match.group(2))
            end_idx = int(range_match.group(3))
            print(f"DEBUG: Range selector: {tag}[{start_idx}-{end_idx}]")
            elements = element.find_all(tag)
            print(f"DEBUG: Found {len(elements)} {tag} elements for range [{start_idx}-{end_idx}]")
            result = []
            for idx in range(start_idx, end_idx + 1):
                if idx < len(elements):
                    result.append(elements[idx])
            print(f"DEBUG: Returning {len(result)} elements from range")
            return result
        
        
        single_match = re.match(r'([\w-]+):\[(\d+)\]', part)
        if single_match:
            tag = single_match.group(1)
            idx = int(single_match.group(2))
            print(f"DEBUG: Single index selector: {tag}[{idx}]")
            elements = element.find_all(tag)
            print(f"DEBUG: Found {len(elements)} {tag} elements")
            if len(elements) > idx:
                return elements[idx]
            print(f"DEBUG: Index {idx} out of range for {tag} (max: {len(elements)-1})")
            return None
        
        
        elif part.startswith('[') and ']' in part:
            print(f"DEBUG: Text array selector: {part}")
            return self._parse_and_find_text_array(element, part)
        
        
        elif part.startswith('"') and part.endswith('"'):
            search_text = part[1:-1]
            print(f"DEBUG: Text selector: '{search_text}'")
            return self._find_element_by_text(element, [search_text], 0)
        
        
        elif part.startswith('~'):
            offset_str = part[1:]
            try:
                offset = int(offset_str)
                print(f"DEBUG: Sibling selector: ~{offset}")
                return self._find_sibling_by_offset(element, offset)
            except ValueError:
                print(f"DEBUG: Invalid sibling offset: {offset_str}")
                return None
        
        
        elif ':' in part:
            
            if '.' in part:
                
                tag_class_part, index_str = part.split(':', 1)
                
                if '.' in tag_class_part:
                    tag, class_name = tag_class_part.split('.', 1)
                    print(f"DEBUG: Tag/class/index selector: {tag}.{class_name}:{index_str}")
                    elements = element.find_all(tag, class_=class_name)
                    print(f"DEBUG: Found {len(elements)} {tag} elements with class '{class_name}'")
                    if elements and int(index_str) < len(elements):
                        return elements[int(index_str)]
                    print(f"DEBUG: Index {index_str} out of range for {tag}.{class_name}")
                    return None
                else:
                    
                    tag, index = part.split(':')
                    print(f"DEBUG: Tag/index selector: {tag}:{index}")
                    elements = element.find_all(tag)
                    print(f"DEBUG: Found {len(elements)} {tag} elements")
                    if len(elements) <= int(index):
                        print(f"DEBUG: Index {index} out of range for {tag} (max: {len(elements)-1})")
                        return None
                    return elements[int(index)]
            else:
                
                tag, index = part.split(':')
                print(f"DEBUG: Tag/index selector: {tag}:{index}")
                elements = element.find_all(tag)
                print(f"DEBUG: Found {len(elements)} {tag} elements")
                if len(elements) <= int(index):
                    print(f"DEBUG: Index {index} out of range for {tag} (max: {len(elements)-1})")
                    return None
                return elements[int(index)]
        
        
        else:
            print(f"DEBUG: Simple tag selector: {part}")
            elements = element.find_all(part)
            print(f"DEBUG: Found {len(elements)} {part} elements")
            return elements[0] if elements else None

    def _find_elements_by_range(self, element, tag, start_idx, end_idx):
        """Находит элементы в указанном диапазоне индексов"""
        elements = element.find_all(tag)
        print(f"DEBUG: Found {len(elements)} {tag} elements for range [{start_idx}-{end_idx}]")
        result = []
        for idx in range(start_idx, end_idx + 1):
            if idx < len(elements):
                result.append(elements[idx])
        print(f"DEBUG: Returning {len(result)} elements from range")
        return result

    def _find_container_alternative(self, soup, fallback_pattern):
        """Альтернативные методы поиска контейнера"""
        if fallback_pattern:
            print(f"DEBUG: Trying fallback pattern: {fallback_pattern}")
            return self._find_pre_pattern(soup, fallback_pattern)
        
        
        print("DEBUG: Trying alternative container search...")
        
        
        common_containers = soup.find_all(class_=re.compile(r'card-list|container|wrapper|content'))
        if common_containers:
            print(f"DEBUG: Found {len(common_containers)} common containers")
            return [common_containers[0]]
            
        return None

    def _debug_dom_structure(self, soup, pattern):
        """Выводит отладочную информацию о структуре DOM"""
        print("DEBUG: === DOM STRUCTURE ANALYSIS ===")
        
        
        parts = pattern.split('/')
        current = soup
        
        for i, part in enumerate(parts):
            print(f"DEBUG: Step {i}: '{part}'")
            
            if part == '':
                continue
                
            if part.startswith('"') and part.endswith('"'):
                
                search_text = part[1:-1]
                print(f"DEBUG: Searching for text: '{search_text}'")
                elements_with_text = current.find_all(string=re.compile(re.escape(search_text), re.IGNORECASE))
                print(f"DEBUG: Found {len(elements_with_text)} text matches")
                for j, elem in enumerate(elements_with_text):
                    print(f"DEBUG: Text match {j}: '{elem}'")
                    if hasattr(elem, 'parent'):
                        print(f"DEBUG: Parent: {elem.parent.name}")
                
            elif ':' in part and not part.startswith('['):
                
                tag, index = part.split(':')
                elements = current.find_all(tag)
                print(f"DEBUG: Found {len(elements)} '{tag}' elements")
                for j, elem in enumerate(elements):
                    print(f"DEBUG: {tag} {j}: {elem.name} class={elem.get('class', '')} id={elem.get('id', '')}")
                    
            elif part.startswith('~'):
                
                print(f"DEBUG: Sibling navigation: {part}")
                if hasattr(current, 'find_next_sibling'):
                    next_sib = current.find_next_sibling()
                    prev_sib = current.find_previous_sibling()
                    print(f"DEBUG: Next sibling: {getattr(next_sib, 'name', 'None')}")
                    print(f"DEBUG: Previous sibling: {getattr(prev_sib, 'name', 'None')}")
        
        print("DEBUG: === END DOM ANALYSIS ===")

    def _resolve_rules(self, task_rules):
        resolved = []
        for rule in task_rules:
            if 'id' in rule:
                if rule['id'] in self.rulesets:
                    
                    ruleset_rules = self.rulesets[rule['id']]['rules']
                    for r in ruleset_rules:
                        resolved_rule = r.copy()
                        if 'rule' in resolved_rule:
                            resolved_rule['rule'] = self._substitute_variables(resolved_rule['rule'])
                        resolved.append(resolved_rule)
                else:
                    print(f"Warning: Ruleset '{rule['id']}' not found")
            elif 'rule' in rule:
                
                resolved_rule = rule.copy()
                resolved_rule['rule'] = self._substitute_variables(resolved_rule['rule'])
                resolved.append(resolved_rule)
            else:
                print(f"Warning: Invalid rule format: {rule}")
        return resolved

    def _substitute_variables(self, rule):
        """Заменяет переменные в правиле на их значения"""
        if not rule:
            return rule
        
        pattern = r'\$\{([^}]+)\}'
        
        def replace_match(match):
            var_name = match.group(1)
            if var_name in self.variables:
                return self.variables[var_name]
            else:
                print(f"Warning: Variable '{var_name}' not found")
                return match.group(0)  
        
        
        new_rule = re.sub(pattern, replace_match, rule)
        
        
        while re.search(pattern, new_rule) and new_rule != rule:
            rule = new_rule
            new_rule = re.sub(pattern, replace_match, rule)
        
        return new_rule

    def _parse_container(self, container, rules, setnull, base_url, limit=None, include_headers=False, row_selector='tr'):
        """Универсальный парсинг контейнера с поддержкой разных селекторов строк"""
        data = []
        
        print(f"DEBUG: Parsing container with row_selector: {row_selector}")
        
        
        if isinstance(container, list):
            if container:
                container = container[0]  
            else:
                print("DEBUG: Container is empty list")
                return data
        
        
        if ':' in row_selector:
            
            tag, index = row_selector.split(':')
            rows = container.find_all(tag)
            print(f"DEBUG: Found {len(rows)} '{tag}' elements")
            if rows and int(index) < len(rows):
                rows = [rows[int(index)]]
                print(f"DEBUG: Using element at index {index}")
            else:
                rows = []
                print(f"DEBUG: Index {index} out of range")
        elif '.' in row_selector:
            
            tag, class_name = row_selector.split('.', 1)
            rows = container.find_all(tag, class_=class_name)
            print(f"DEBUG: Found {len(rows)} '{tag}' elements with class '{class_name}'")
        else:
            
            rows = container.find_all(row_selector)
            print(f"DEBUG: Found {len(rows)} '{row_selector}' elements")
        
        if not rows:
            print("DEBUG: No rows found in container")
            return data
        
        
        start_index = 0 if include_headers else 0  
        
        
        rows_to_process = rows[start_index:]
        if limit is not None:
            rows_to_process = rows_to_process[:limit]
            print(f"DEBUG: Limiting to {limit} rows")
        
        print(f"DEBUG: Processing {len(rows_to_process)} rows")
        
        for i, row in enumerate(rows_to_process):
            print(f"DEBUG: Processing row {i}")
            row_data = {}
            for rule in rules:
                value = self._apply_rule(row, rule['rule'], setnull, base_url)
                row_data[rule['name']] = value
            
            if any(v != 'NULL' for v in row_data.values()):
                data.append(row_data)
        
        print(f"DEBUG: Extracted {len(data)} records from container")
        return data

    
    
    
    
    

    def _apply_rule(self, element, rule, setnull, base_url):
        try:
            
            if '&href' in rule:
                return self._apply_rule_with_href(element, rule, setnull, base_url)
            else:
                return self._apply_complex_rule(element, rule, setnull)
                
        except (IndexError, AttributeError, ValueError) as e:
            return 'NULL' if setnull else ''

    def _apply_rule_with_href(self, element, rule, setnull, base_url):
        
        href_part, remaining_rule = rule.split('&href', 1)
        
        
        if remaining_rule.startswith('/'):
            remaining_rule = remaining_rule[1:]
        
        
        link_element = self._apply_complex_rule_to_find_element(element, href_part)
        if not link_element:
            return 'NULL' if setnull else ''
        
        
        href = link_element.get('href')
        if not href:
            return 'NULL' if setnull else ''
        
        
        detail_url = urljoin(base_url, href)
        
        
        detail_html = self.cache.get_page(detail_url)
        detail_soup = BeautifulSoup(detail_html, 'html.parser')
        
        
        return self._apply_complex_rule(detail_soup, remaining_rule, setnull)

    def _apply_complex_rule(self, element, rule, setnull):
        """Применяет сложное правило с поддержкой поиска по тексту и переходов назад"""
        try:
            current = element
            parts = rule.split('/')
            
            print(f"DEBUG: Applying complex rule: {rule}")
            print(f"DEBUG: Starting element: {getattr(current, 'name', type(current))}")
            
            
            for i, part in enumerate(parts[:-1]):
                print(f"DEBUG: Step {i}: processing part '{part}'")
                current = self._process_rule_part(current, part)
                if current is None:
                    print(f"DEBUG: Step {i}: part '{part}' returned None")
                    return 'NULL' if setnull else ''
                print(f"DEBUG: Step {i}: found element {getattr(current, 'name', type(current))}")
            
            
            last_part = parts[-1]
            print(f"DEBUG: Final step: extracting from last part '{last_part}'")
            result = self._extract_from_last_part(current, last_part, setnull)
            print(f"DEBUG: Final result: '{result}'")
            return result
                
        except (IndexError, AttributeError, ValueError) as e:
            print(f"DEBUG: Error in _apply_complex_rule: {e}")
            import traceback
            traceback.print_exc()
            return 'NULL' if setnull else ''

    def _apply_complex_rule_to_find_element(self, element, rule):
        """Применяет правило для поиска элемента (без извлечения значения)"""
        try:
            current = element
            parts = rule.split('/')
            
            for part in parts:
                current = self._process_rule_part(current, part)
                if current is None:
                    return None
                    
            return current
        except (IndexError, AttributeError, ValueError):
            return None

    def _process_rule_part(self, element, part):
        """Обрабатывает одну часть правила: навигацию или поиск по тексту"""
        print(f"DEBUG: Processing rule part: '{part}'")
        
        if part == '..':
            
            return element.parent if element.parent else None
        
        elif part.startswith('~'):
            
            offset_str = part[1:]
            try:
                offset = int(offset_str)
                return self._find_sibling_by_offset(element, offset)
            except ValueError:
                return None
        
        elif part.startswith('[') and ']' in part:
            
            return self._parse_and_find_text_array(element, part)
        
        elif part.startswith('"') and part.endswith('"'):
            
            search_text = part[1:-1]
            return self._find_element_by_text(element, [search_text], 0)
        
        
        elif part.startswith('
            element_id, index_str = part[1:].split(':', 1)
            try:
                index = int(index_str)
                return self._find_element_by_id(element, element_id, index)
            except ValueError:
                return None
        elif part.startswith('
            element_id = part[1:]
            return self._find_element_by_id(element, element_id, 0)
        
        elif '"' in part and ':' in part:
            
            match = re.match(r'"([^"]+)"(?::(\d+))?', part)
            if match:
                search_text = match.group(1)
                index = int(match.group(2)) if match.group(2) else 0
                return self._find_element_by_text(element, [search_text], index)
        
        
        elif '.' in part and ':' in part:
            
            tag_class, index_str = part.split(':', 1)
            if '.' in tag_class:
                tag, class_name = tag_class.split('.', 1)
                try:
                    index = int(index_str)
                    elements = element.find_all(tag, class_=class_name)
                    print(f"DEBUG: Found {len(elements)} {tag} elements with class '{class_name}'")
                    if elements and index < len(elements):
                        return elements[index]
                except ValueError:
                    pass
            return None
        
        elif '.' in part:
            
            tag, class_name = part.split('.', 1)
            elements = element.find_all(tag, class_=class_name)
            print(f"DEBUG: Found {len(elements)} {tag} elements with class '{class_name}'")
            return elements[0] if elements else None
        
        
        else:
            if ':' in part:
                tag, index = part.split(':')
                elements = element.find_all(tag)
                if len(elements) <= int(index):
                    return None
                return elements[int(index)]
            else:
                
                elements = element.find_all(part)
                return elements[0] if elements else None
        
        return None

    def _parse_and_find_text_array(self, element, part):
        """Парсит массив текстов и находит соответствующий элемент"""
        try:
            
            array_end = part.rfind(']')
            array_str = part[:array_end+1]
            index_str = part[array_end+1:]
            
            
            if index_str.startswith(':'):
                index_str = index_str[1:]
            
            
            texts = yaml.safe_load(array_str)
            if not isinstance(texts, list):
                texts = [texts]
            
            
            index = 0
            if index_str:
                try:
                    index = int(index_str)
                except ValueError:
                    index = 0
            
            
            return self._find_element_by_text(element, texts, index)
            
        except Exception as e:
            print(f"Error parsing text array: {e}")
            return None

    def _find_sibling_by_offset(self, element, offset):
        """Находит соседний элемент с указанным смещением"""
        if offset == 0:
            return element
        
        current = element
        if offset > 0:
            
            for _ in range(offset):
                current = current.find_next_sibling()
                if current is None:
                    return None
        else:
            
            for _ in range(-offset):
                current = current.find_previous_sibling()
                if current is None:
                    return None
        
        return current
    def _find_element_by_id(self, element, element_id, index=0):
        """Находит элемент по ID"""
        elements = element.find_all(id=element_id)
        print(f"DEBUG: Found {len(elements)} elements with id '{element_id}'")
        
        if elements and index < len(elements):
            return elements[index]
        return None
    
    def _find_element_by_text(self, element, search_texts, index=0):
        """Находит элемент, содержащий указанный текст (с поддержкой массива текстов)"""
        
        all_elements = []
        
        for search_text in search_texts:
            
            elements_with_text = element.find_all(
                string=lambda text: text and text.strip() == search_text
            )
            
            
            filtered_elements = []
            for elem in elements_with_text:
                
                parent = elem.parent
                skip = False
                while parent and parent != element:
                    if parent.name in ['script', 'style', 'noscript']:
                        skip = True
                        break
                    
                    if parent.get('style') and 'display:none' in parent.get('style'):
                        skip = True
                        break
                    if parent.get('class') and any('hidden' in cls for cls in parent.get('class')):
                        skip = True
                        break
                    parent = parent.parent
                
                if not skip:
                    filtered_elements.append(elem)
            
            all_elements.extend(filtered_elements)
        
        
        seen = set()
        unique_elements = []
        for elem in all_elements:
            if elem not in seen:
                seen.add(elem)
                unique_elements.append(elem)
        
        print(f"DEBUG: Found {len(unique_elements)} elements with exact text '{search_texts}' after filtering")
        for i, elem in enumerate(unique_elements):
            parent_info = f" (parent: {elem.parent.name})" if elem.parent else ""
            print(f"DEBUG: Element {i}: '{elem.strip()}'{parent_info}")
        
        if unique_elements and index < len(unique_elements):
            
            return unique_elements[index].parent
        
        return None

    def _extract_from_last_part(self, element, last_part, setnull):
        """Извлекает значение из последней части правила"""
        try:
            print(f"DEBUG: Extracting from last part: '{last_part}'")
            
            
            if last_part.startswith('[') and ']' in last_part:
                
                element_with_text = self._parse_and_find_text_array(element, last_part)
                if element_with_text:
                    return self._extract_value(element_with_text, 'text')
                else:
                    return 'NULL' if setnull else ''
            
            elif last_part.startswith('"') and '"' in last_part[1:]:
                
                match = re.match(r'"([^"]+)"(?::(\d+))?(?::(\w+))?', last_part)
                if match:
                    search_text = match.group(1)
                    index = int(match.group(2)) if match.group(2) else 0
                    attr = match.group(3) or 'text'
                    
                    element_with_text = self._find_element_by_text(element, [search_text], index)
                    if element_with_text:
                        return self._extract_value(element_with_text, attr)
                    else:
                        return 'NULL' if setnull else ''
            
            
            elif last_part.startswith('
                
                parts = last_part[1:].split(':')
                element_id = parts[0]
                index = int(parts[1]) if len(parts) > 1 else 0
                attr = parts[2] if len(parts) > 2 else 'text'
                
                element_by_id = self._find_element_by_id(element, element_id, index)
                if element_by_id:
                    return self._extract_value(element_by_id, attr)
            
            elif last_part.startswith('
                
                if ':' in last_part:
                    element_id, attr = last_part[1:].split(':', 1)
                else:
                    element_id = last_part[1:]
                    attr = 'text'
                
                element_by_id = self._find_element_by_id(element, element_id, 0)
                if element_by_id:
                    return self._extract_value(element_by_id, attr)
            
            
            elif '.' in last_part and ':' in last_part:
                
                parts = last_part.split(':')
                if len(parts) >= 2:
                    tag_class = parts[0]
                    if '.' in tag_class:
                        tag, class_name = tag_class.split('.', 1)
                        index = int(parts[1]) if len(parts) > 1 else 0
                        attr = parts[2] if len(parts) > 2 else 'text'
                        
                        elements = element.find_all(tag, class_=class_name)
                        print(f"DEBUG: Found {len(elements)} {tag} elements with class '{class_name}' for extraction")
                        if elements and index < len(elements):
                            return self._extract_value(elements[index], attr)
            
            elif '.' in last_part:
                
                if ':' in last_part:
                    tag_class, attr = last_part.split(':', 1)
                else:
                    tag_class = last_part
                    attr = 'text'
                
                if '.' in tag_class:
                    tag, class_name = tag_class.split('.', 1)
                    elements = element.find_all(tag, class_=class_name)
                    print(f"DEBUG: Found {len(elements)} {tag} elements with class '{class_name}' for extraction")
                    if elements:
                        return self._extract_value(elements[0], attr)
            
            
            if ':' in last_part:
                parts = last_part.split(':')
                if len(parts) == 2:
                    
                    tag, index = parts
                    elements = element.find_all(tag)
                    if len(elements) > int(index):
                        return self._extract_value(elements[int(index)], 'text')
                elif len(parts) == 3:
                    
                    tag, index, attr = parts
                    elements = element.find_all(tag)
                    if len(elements) > int(index):
                        return self._extract_value(elements[int(index)], attr)
            else:
                
                return self._extract_value(element, 'text')
                
        except (IndexError, AttributeError, ValueError) as e:
            print(f"DEBUG: Error in _extract_from_last_part: {e}")
            return 'NULL' if setnull else ''
        
        return 'NULL' if setnull else ''

    def _extract_value(self, element, attr):
        if attr == 'text':
            return element.get_text(strip=True)
        return element.get(attr, '')