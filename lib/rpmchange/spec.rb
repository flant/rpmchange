module Rpmchange
  class Spec
    class << self
      def load(str)
        Spec.new(str)
      end

      def loadfile(path)
        Spec.new(Pathname.new(path).read)
      end

      def diff(a, b, **kwargs)
        Diffy::Diff.new(a.to_s, b.to_s, {diff: "-U 3"}.merge(kwargs))
      end

      def without_macro
      end
    end # << self

    attr_reader :str

    def initialize(str)
      @str = str
      _load!
    end

    def reload
      @sections = nil
    end

    def dump
      [].tap do |res|
        res.push *preamble_lines
        sections.each do |section, by_params|
          by_params.each {|params, lines|
            res.push ["%#{section}", *params].join(' ')
            res.push *lines
          }
        end
      end.map {|line| line + "\n"}.join
    end

    def to_s
      dump
    end

    def inspect
      "#<#{self.class}: #{name}/#{full_version}>"
    end

    def diff(with: nil, **kwargs)
      if with
        self.class.diff(dump, with, **kwargs)
      else
        self.class.diff(str, dump, **kwargs)
      end
    end

    def name
      tag(:name)
    end

    def name=(value)
      set_tag(:name, value)
    end

    def version
      tag(:version)
    end

    def version=(value)
      set_tag(:version, value)
    end

    def release
      tag(:release)
    end

    def release=(value)
      set_tag(:release, value)
    end

    def epoch
      tag(:epoch)
    end

    def epoch=(value)
      set_tag(:epoch, value)
    end

    def full_version
      [epoch, [version, release].compact.join('-')]
        .compact
          .join(':')
            .gsub(/%{.*}/, '')
    end

    def append_changelog(name:, email:, message:)
      message_lines = message.to_s.split("\n")
      message_lines[0] = "- #{message_lines[0]}"
      1.upto(message_lines.size - 1).each do |i|
        message_lines[i] = "  #{message_lines[i]}"
      end

      ["* #{Time.now.strftime("%a %b %e %Y")} #{name} <#{email}> - #{full_version}",
        message_lines.join("\n"),
        "",
      ].reverse_each {|line| _prepend_line(lines: changelog_lines, new_line: line)}
    end

    def to_tag_name(tag)
      tag.to_s.capitalize
    end

    def tag(tag)
      match = preamble_lines.find {|line| line.start_with? "#{to_tag_name(tag)}:"}
      res = match.split(':', 2).last if match
      res.strip if res
    end

    def set_tag(tag, value)
      _replace_line(lines: preamble_lines, new_line: "#{to_tag_name(tag)}: #{value.strip}", match: /#{to_tag_name(tag)}:/)
    end

    def append_tag(tag, value)
      _append_line(lines: preamble_lines, new_line: "#{to_tag_name(tag)}: #{value}")
    end

    def append_patch(value)
      append_patch_macro append_patch_tag(value)
    end

    def patch_tags
      preamble_lines
        .grep(_patch_tag_line_regex)
        .map(&method(:_patch_tag_line_parse))
        .to_h
    end

    def append_patch_tag(value)
      patch_num = nil
      make_line = proc do |insert_ind|
        if insert_ind > 0
          last_patch_num = _patch_tag_line_parse(preamble_lines[insert_ind - 1]).first
          patch_num = last_patch_num + 1
        else
          patch_num = 0
        end
        "Patch#{patch_num}: #{value}"
      end
      _append_line(lines: preamble_lines, new_line: make_line, after: _patch_tag_line_regex)
      patch_num
    end

    def append_patch_macro(num)
      _append_line(lines: prep_lines, new_line: "%patch#{num} -p1", after: _patch_macro_line_regex)
      nil
    end

    def sections
      @sections ||= {}
    end

    def preamble_lines
      @preamble_lines ||= []
    end

    SECTIONS = %i{prep build install clean check files changelog}
    SECTIONS.each do |section|
      define_method("#{section}_lines") {|params=nil| (sections[section] || {})[params] || []}
    end

    protected

    def _patch_macro_line_regex
      @_patch_macro_line_regex ||= /^%patch[0-9]*/
    end

    def _append_line(lines:, new_line:, after: nil)
      find_index = proc do |lines|
        if after
          ind = lines.rindex {|line| line.to_s =~ after}
          ind ? ind + 1 : -1
        else
          -1
        end
      end
      _insert_line(lines: lines, new_line: new_line, find_index: find_index)
    end

    def _prepend_line(lines:, new_line:, before: nil)
      find_index = proc do |lines|
        if before
          lines.index {|line| line.to_s =~ before} || 0
        else
          0
        end
      end
      _insert_line(lines: lines, new_line: new_line, find_index: find_index)
    end

    def _insert_line(lines:, new_line:, find_index:)
      if ind = find_index.call(lines)
        line = (new_line.respond_to?(:call) ? new_line.call(ind) : new_line).to_s.chomp
        lines.insert(ind, line)
      end
    end

    def _replace_line(lines:, new_line:, match:)
      if ind = lines.index {|line| line.to_s =~ match}
        line = (new_line.respond_to?(:call) ? new_line.call(ind) : new_line).to_s.chomp
        lines[ind] = line
      end
    end

    def _patch_tag_line_parse(line)
      tag, value = line.split(':', 2)
      [tag.split('Patch').last.to_i, value.strip] if tag
    end

    def _patch_tag_line_regex
      @_patch_tag_line_regex ||= /^Patch[0-9]*:/
    end

    def _load!
      current_section = preamble_lines
      str.lines.each do |line|
        line.chomp!
        if section = SECTIONS.find {|s| line.start_with? "%#{s}"}
          section_params = line.split(' ')[1..-1]
          section_key = section_params.empty? ? nil : section_params
          sections[section] ||= {}
          sections[section][section_key] ||= []
          current_section = sections[section][section_key]
        else
          current_section << line
        end
      end
    end
  end # Spec
end # Rpmchange
