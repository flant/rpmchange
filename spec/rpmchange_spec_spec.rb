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

      spec.append_changelog name: 'Test', email: 'test@test.com', message: 'Test release'
      expect(spec.dump).not_to eq(orig_content)
      expect(spec.diff(diff: "-U 0").to_s).to eq <<-ENTRY
+* #{Time.now.strftime("%a %b %e %Y")} Test <test@test.com> - #{spec.full_version}
+- Test release
+
      ENTRY
    end
  end
end
