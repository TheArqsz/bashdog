# {{ project_name }} Documentation

## Table of Contents
{% for module in modules %}
- [**{{ module.name }}**](#{{ module.id }})
  {% if module.functions %}
    <ul>
    {% for func in module.functions %}
      <li><a href="#{{ func.id }}">{{ func.name }}()</a></li>
    {% endfor %}
    </ul>
  {% endif %}
{% endfor %}

{% for module in modules %}

<h2 id="{{ module.id }}">Module: {{ module.name }}</h2>

{% if module.author %}**Author:** {{ module.author | join('') | trim }}{% endif %}

{% if module.description %}

### Description

{{ module.description | join('') | trim }}

{% endif %}

{% if module.usage %}
### Usage
```bash
{{ module.usage | join('') | trim }}
```
{% endif %}

{% if module.functions %}
## Functions

{% for func in module.functions %}

<h4 id="{{ func.id }}"><code>{{ func.name }}</code></h4>

{{ func.description |join('') }}

{% if func.arg %}

#### Arguments

| Name | Type | Description |
|------|-------------|-------------|
{% for arg in func.arg %}
| `{{ arg.name }}` | *{{ arg.type }}* | {{ arg.description }} |
{% endfor %}

{% endif %}

{% if func.globals %}

#### Global Variables:

| Name | Type | Description |
|------|-------------|-------------|
{% for global in func.globals %}
| `{{ global.name }}` | *{{ global.type }}* | {{ global.description }} |
{% endfor %}

{% endif %}

{% if func.example %}

#### Example:

```bash
{{ func.example |join('') |trim}}
```

{% endif %}

{% if func.returns %}

#### Returns:

<p>{{ func.returns |join('') }}</p>

{% endif %}

{% endfor %}
{% endif %}
{% endfor %}