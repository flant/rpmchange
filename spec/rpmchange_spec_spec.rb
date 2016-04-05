describe Rpmchange::Spec do
  include SpecHelper::Common
  include SpecHelper::Fixture

  it 'dumps spec without any change' do
    fixture_rpmspec_each do |spec, path|
      orig_content = path.read
      expect(spec.dump).to eq(orig_content)
    end
  end

  it 'changes version' do
    fixture_rpmspec_each do |spec, path|
      orig_content = path.read
      orig_spec = spec_load(orig_content)
      orig_version_parts = orig_spec.version.split('.')

      new_version_parts = orig_version_parts.dup
      new_version_parts[-1] = (new_version_parts[-1].to_i + 1).to_s
      new_version = new_version_parts.join('.')

      spec.version = new_version
      expect(spec.version).to eq(new_version)
      expect(spec.dump).not_to eq(orig_content)

      spec.version = orig_spec.version
      expect(spec.version).to eq(orig_spec.version)
    end
  end

  it 'appends changelog' do
    fixture_rpmspec_each do |spec, path|
      orig_content = path.read
      orig_spec = spec_load(orig_content)

      name, email, message = ['Test', 'test@test.com', 'Test release']
      spec.append_changelog name: name, email: email, message: message
      expect(spec.dump).not_to eq(orig_content)
      expect(spec.diff(diff: "-U 0").to_s).to eq <<-ENTRY
+* #{Time.now.strftime("%a %b %e %Y")} #{name} <#{email}> - #{spec.full_version}
+- #{message}
+
      ENTRY
    end
  end

  it 'appends lines to each section' do
    fixture_rpmspec_each do |spec, path|
      spec.class::SECTIONS.each do |section|
        next unless spec.section? section

        spec.append(section: section, value: "line1\nline2")
        expect(spec.section_lines(section)[-2]).to eq("line1")
        expect(spec.section_lines(section)[-1]).to eq("line2")

        spec.prepend(section: section, value: "\nline3\nline4\n")
        expect(spec.section_lines(section)[0]).to eq("")
        expect(spec.section_lines(section)[1]).to eq("line3")
        expect(spec.section_lines(section)[2]).to eq("line4")

        spec.append(section: section, value: "line5\nline6", after: /^line4$/)
        expect(spec.section_lines(section)[3]).to eq("line5")
        expect(spec.section_lines(section)[4]).to eq("line6")

        spec.delete(section: section, match: /^line4$/)
        expect(spec.section_lines(section)[2]).to eq("line5")

        spec.prepend(section: section, value: "line7\nline8", before: /^line5$/)
        expect(spec.section_lines(section)[2]).to eq("line7")
        expect(spec.section_lines(section)[3]).to eq("line8")

        spec.replace(section: section, value: "line eight\nline nine", match: /^line8$/)
        expect(spec.section_lines(section)[3]).to eq("line eight")
        expect(spec.section_lines(section)[4]).to eq("line nine")
      end
    end
  end
end
