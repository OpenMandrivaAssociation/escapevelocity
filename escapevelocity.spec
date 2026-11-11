Name:		escapevelocity
Version:	1.1
Release:	1
Summary:	Subset of the Velocity template language
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/google/escapevelocity
Source0:	https://github.com/google/escapevelocity/archive/refs/tags/escapevelocity-%{version}.tar.gz#/escapevelocity-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	mvn(com.google.guava:guava)

%description
EscapeVelocity %{version} evaluates a subset of Apache Velocity templates.
AutoValue uses it to generate Java sources.

%prep
%autosetup -n escapevelocity-escapevelocity-%{version} -p1
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
find src/main/java -name '*.java' ! -name 'module-info.java' > sources.list
test "$(wc -l < sources.list)" -eq 16
mkdir -p classes
javac --release 8 -encoding UTF-8 \
	-cp %{_javadir}/guava.jar:%{_javadir}/failureaccess.jar \
	-d classes @sources.list
jar cf escapevelocity.jar -C classes .
jar tf escapevelocity.jar | grep -E '\.(java|jar|so|node|wasm)$' && exit 1 || true
javap -verbose -cp escapevelocity.jar com.google.escapevelocity.Template | grep -F 'major version: 52'

cat > escapevelocity.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.google.escapevelocity</groupId>
  <artifactId>escapevelocity</artifactId>
  <version>1.1</version>
  <name>EscapeVelocity</name>
  <description>Subset of the Velocity template language</description>
  <licenses>
    <license>
      <name>Apache-2.0</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.google.guava</groupId>
      <artifactId>guava</artifactId>
      <version>33.6.0-jre</version>
    </dependency>
  </dependencies>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact escapevelocity.pom:escapevelocity.jar \
	--file-name escapevelocity \
	--filelist .mfiles

%check
mkdir -p check
cat > check/Smoke.java << 'END'
import com.google.escapevelocity.Template;
import java.io.StringReader;
import java.util.HashMap;
public class Smoke {
	public static void main(String[] args) throws Exception {
		Template template = Template.parseFrom(new StringReader("Hello $name"));
		HashMap<String, Object> vars = new HashMap<String, Object>();
		vars.put("name", "ev");
		System.out.println("escapevelocity_ok " + template.evaluate(vars));
	}
}
END
JAR=%{buildroot}%{_javadir}/escapevelocity.jar
test -f "$JAR"
CP="$JAR:%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar"
javac --release 8 -encoding UTF-8 -cp "$CP" -d check check/Smoke.java
java -cp "check:$CP" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'escapevelocity_ok Hello ev' check/out.txt

%files -f .mfiles
%doc LICENSE NOTICE README.md
