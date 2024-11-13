import matplotlib.pyplot as plt
import numpy as np


def func(r, n , w):
    xml_text = r*(2*n + 5) + 7
    xml_attr = 8 * r + 4
    hymeko = 4*r + 4
    yaml_tags = r * ((w+2)+(2*(3+w)))
    yaml_value = (3 + 2)*r + 4
    json_tags = 14*r + 6
    json_values = 7*r + 4
    return xml_text, xml_attr, hymeko, yaml_tags, yaml_value, json_tags, json_values

def main():
    fontsize = 24
    fontsize_legend = 20
    n = 1
    r = np.arange(1, 1000+1)
    xlabel_text = 'Number of hyperarcs'
    xml_text, xml_attr, hymeko, yaml_tags, yaml_value, json_tags, json_values = func(r, n, 1)

    plt.figure(figsize=(10, 15))

    plt.plot(r, xml_text, label='XML Text')
    plt.plot(r, xml_attr, label='XML Attribute')
    plt.plot(r, hymeko, label='Himeko', linewidth=2)
    plt.plot(r, yaml_tags, label='YAML Tags')
    plt.plot(r, yaml_value, label='YAML Value', linestyle='--')
    plt.plot(r, json_tags, label='JSON Tags')
    plt.plot(r, json_values, label='JSON Values', linestyle='--')

    plt.xlabel(xlabel_text, fontsize=fontsize_legend)
    plt.ylabel('Line size', fontsize=fontsize_legend)
    plt.title('Description size of hypergraphs (lines)', fontsize=fontsize_legend)

    # Increase tick label font size
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    plt.legend(fontsize=fontsize)
    plt.grid()
    plt.show()
    r = np.arange(0, 20000)
    xml_text, xml_attr, hymeko, yaml_tags, yaml_value, json_tags, json_values = func(r, n, 1)

    plt.figure(figsize=(10, 15))
    plt.loglog(r, xml_text, label='XML Text')
    plt.loglog(r, xml_attr, label='XML Attribute')
    plt.loglog(r, hymeko, label='Himeko', linewidth=2)
    plt.loglog(r, yaml_tags, label='YAML Tags')
    plt.loglog(r, yaml_value, label='YAML Value', linestyle='--')
    plt.loglog(r, json_tags, label='JSON Tags')
    plt.loglog(r, json_values, label='JSON Values', linestyle='--')


    plt.xlabel(xlabel_text, fontsize=fontsize_legend)
    plt.ylabel('Line size', fontsize=fontsize_legend)
    plt.title('Description size of hypergraphs (lines) log', fontsize=fontsize_legend)

    # Increase tick label font size
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    plt.legend(fontsize=fontsize)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
