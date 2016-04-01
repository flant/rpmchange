module Rpmchange
  class Cli < ::Thor
    class << self
      def shared_options
        (@shared_options || {}).each do |name, options|
          method_option name, options
        end
      end

      def construct_spec(options)
        Spec.new(options['specfile'])
      end
    end # << self

    @shared_options = {
      specfile: {type: :string, desc: "path to spec file", required: true},
    }

    desc "append_changelog", "Make a new changelog entry at the end of current entries"
    shared_options
    method_option :name, {type: :string, desc: "maintainer name", required: true}
    method_option :email, {type: :string, desc: "maintainer email", required: true}
    method_option :message, {type: :string, desc: "changelog message", required: true}
    def append_changelog
      spec = self.class.construct_spec(options)
      spec.append_changelog(name: options['name'],
                            email: options['email'],
                            message: options['message'])
      spec.save!
    end
  end # Cli
end # Rpmchange
